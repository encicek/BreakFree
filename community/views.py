from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Post
from .forms import PostForm, CommentForm


def community_home(request):
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'community/community_home.html', {'posts': posts})


@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)

        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect('community_home')
    else:
        form = PostForm()

    return render(request, 'community/create_post.html', {'form': form})


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all().order_by('-created_at')

    if request.method == 'POST':
        comment_form = CommentForm(request.POST)

        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.user = request.user
            comment.save()
            return redirect('post_detail', post_id=post.id)
    else:
        comment_form = CommentForm()

    return render(request, 'community/post_detail.html', {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
    })
