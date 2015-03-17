from django import forms
from django.core.exceptions import ValidationError
from django.db import transaction, connection
from django.forms import ModelForm
from django.http import HttpResponseRedirect
from django.views.generic import View
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.detail import SingleObjectMixin

from judge.models import CommentMPTT


class CommentForm(ModelForm):
    class Meta:
        model = CommentMPTT
        fields = ['title', 'body', 'parent']
        widgets = {
            'parent': forms.HiddenInput(),
        }

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super(CommentForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({'style': 'min-width:100%', 'placeholder': 'Comment title'})
        self.fields['body'].widget.attrs.update({'style': 'min-width:100%', 'placeholder': 'Comment body'})

    def clean(self):
        if self.request is not None and self.request.user.is_authenticated() and self.request.user.profile.mute:
            raise ValidationError('You are not allowed to comment...')
        return super(CommentForm, self).clean()


class CommentedDetailView(TemplateResponseMixin, SingleObjectMixin, View):
    comment_page = None

    def get_comment_page(self):
        if self.comment_page is None:
            raise NotImplementedError()
        return self.comment_page

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        page = self.get_comment_page()

        cursor = connection.cursor()
        auto_commit = transaction.get_autocommit()
        try:
            transaction.set_autocommit(False)
            cursor.execute('LOCK TABLES judge_commentmptt WRITE, judge_profile READ')

            form = CommentForm(request, request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.author = request.user.profile
                comment.page = page
                comment.save()
                return HttpResponseRedirect(request.path)
        except:
            transaction.rollback()
            raise
        else:
            transaction.commit()
        finally:
            transaction.set_autocommit(auto_commit)
            cursor.execute('UNLOCK TABLES')

        context = self.get_context_data(object=self.object, comment_form=form)
        return self.render_to_response(context)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return self.render_to_response(self.get_context_data(
            object=self.object,
            comment_form=CommentForm(request, initial={'page': self.get_comment_page(), 'parent': None})
        ))

    def get_context_data(self, **kwargs):
        context = super(CommentedDetailView, self).get_context_data(**kwargs)
        context['comment_list'] = CommentMPTT.objects.filter(page=self.get_comment_page())
        return context
