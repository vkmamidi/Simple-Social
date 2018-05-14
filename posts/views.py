from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin

from django.core.urlresolvers import reverse_lazy,reverse
from django.http import Http404
from django.views import generic

from braces.views import SelectRelatedMixin

from . import forms
from . import models
from groups.models import Group

from django.contrib.auth import get_user_model
User = get_user_model()


class PostList(SelectRelatedMixin, generic.ListView):
    model = models.Post
    select_related = ("user", "group")


    def get_context_data(self, **kwargs):
        context = super(PostList, self).get_context_data(**kwargs)
        context['user_groups'] = Group.objects.filter(members__in=[self.request.user])
        context['all_groups'] = Group.objects.all()

        return context


class UserPosts(SelectRelatedMixin,generic.ListView):
    model = models.Post
    template_name = "posts/user_post_list.html"
    select_related = ('user','group')

    def get_queryset(self):
        try:
            self.post_user = User.objects.prefetch_related('posts').get(
                username__iexact=self.kwargs.get("username")
            )
        except User.DoesNotExist:
            raise Http404
        else:
            return self.post_user.posts.all()

    def get_context_data(self, **kwargs):
        context = super(UserPosts,self).get_context_data(**kwargs)
        context["post_user"] = self.post_user
        return context


class PostDetail(SelectRelatedMixin, generic.DetailView):
    model = models.Post
    select_related = ("user", "group")

    # def get_queryset(self):
    #     queryset = super(PostDetail,self).get_queryset()
    #     return queryset.filter(
    #         user__username__iexact=self.kwargs.get("username")
    #     )


class CreatePost(LoginRequiredMixin, SelectRelatedMixin, generic.CreateView):
    # form_class = forms.PostForm
    fields = ('message','group')
    model = models.Post

    # def get_form_kwargs(self):
    #     kwargs = super().get_form_kwargs()
    #     kwargs.update({"user": self.request.user})
    #     return kwargs

    def form_valid(self, form):

        self.object = form.save(commit=False)
        self.object.user = self.request.user
        if self.object.user in self.object.group.members.iterator():
            self.object.save()
            return super(CreatePost,self).form_valid(form)
        else:
            messages.warning(self.request,'you are not member of this group')
            raise Http404

class DeletePost(LoginRequiredMixin, SelectRelatedMixin, generic.DeleteView):
    model = models.Post
    select_related = ("user", "group")
    success_url = reverse_lazy("posts:all")

    # def get_queryset(self):
    #     queryset = super(DeletePost,self).get_queryset()
    #     return queryset.filter(user_id=self.request.user.id)

    # def delete(self, *args, **kwargs):
    #     messages.success(self.request, "Post Deleted")
    #     return super(DeletePost,self).delete(*args, **kwargs)
