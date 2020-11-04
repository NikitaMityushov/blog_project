from django.shortcuts import render, get_object_or_404
from .models import Post
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger 
from django.views.generic import ListView


class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'


def post_list(request):
    objects_list = Post.published.all()
    paginator = Paginator(objects_list, 3)  # 3 articles to page
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # if page not an integer return first page
        posts = paginator.page(1)
    except EmptyPage:
        # if page more than overall return last page
        posts = paginator.page(paginator.num_pages)
    context = {'page': page, 'posts': posts}
    return render(request, 'blog/post/list.html', context)


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post, 
                                status='published', 
                                publish__year=year, 
                                publish__month=month,
                                publish__day=day)
    context = {'post': post}
    return render(request, 'blog/post/detail.html', context)