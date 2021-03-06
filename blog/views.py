from django.shortcuts import render,get_object_or_404,redirect
from django.views.generic import (TemplateView,ListView,
                                  DetailView,CreateView,
                                  UpdateView,DeleteView)
from blog.forms import PostForm,CommentForm
from django.urls import reverse_lazy
from django.utils import timezone
from blog.models import Post,Comment
from django.contrib.auth.decorators import login_required # for function based views
from django.contrib.auth.mixins import LoginRequiredMixin # for class based views
from django.contrib.auth.models import User
from blog.forms import UserForm
from django.urls import reverse

# Create your views here.

class AboutView(TemplateView):
    template_name = 'about.html'

class PostListView(ListView):
    model = Post

    def get_queryset(self):
        return Post.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')
''' __lte --> less_than_or_equal,
    order_by('publishd_date') --> asscending order
    order_by('-publishd_date') --> descending order
'''

class PostDetailView(DetailView):
    model = Post

class PostCreateView(LoginRequiredMixin,CreateView):
    login_url = '/accounts/login'
    redirect_field_name = 'blog/post_detail.html'
    form_class = PostForm
    model = Post

class UserCreationView(CreateView):
    template_name = 'registration/user_form.html'
    context_object_name = 'form'
    model = User
    form_class = UserForm

    def get_success_url(self):
        return reverse('login')

class PostUpdateView(LoginRequiredMixin,UpdateView):
    login_url = '/accounts/login'
    redirect_field_name = 'blog/post_detail.html'
    form_class = PostForm
    model = Post

class PostDeleteView(LoginRequiredMixin,DeleteView):
    model = Post
    login_url = '/accounts/login'
    success_url = reverse_lazy('post_draft_list')
    context_object_name = 'form'

class DraftListView(LoginRequiredMixin,ListView):
    login_url = '/accounts/login'
    redirect_field_name = 'blog/post_list.html'
    model = Post
    template_name = 'post_draft_list.html'
    context_object_name = 'posts'

    def get_queryset(self):
        print(Post.objects.filter(published_date__isnull = True).order_by('create_date'))
        return Post.objects.filter(published_date__isnull = True).order_by('create_date')

##########################################################################################3

def add_comment_to_post(request,pk):
    post = get_object_or_404(Post,pk=pk)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit = False)
            comment.post = post
            comment.save()
            return redirect('post_detail',pk=post.pk)
    else:
        form = CommentForm()
    return render(request,'blog/comment_form.html',{'form':form})

@login_required
def comment_approve(request,pk):
    comment = get_object_or_404(Comment,pk = pk)
    comment.approve()
    return redirect('post_detail',pk = comment.post.pk)

@login_required
def comment_remove(request,pk):
    comment = get_object_or_404(Comment,pk=pk)
    post_pk = comment.post.pk
    comment.delete()
    return redirect('post_detail',pk=post_pk)

@login_required
def post_publish(request,pk):
    post = get_object_or_404(Post,pk=pk)
    post.publish()
    return redirect('post_detail',pk=pk)
