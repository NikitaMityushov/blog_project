from django.shortcuts import render, get_object_or_404, redirect
from .models import Post
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger 
from django.views.generic import ListView
from .forms import EmailPostForm, CommentForm
from django.core.mail import send_mail
from taggit.models import Tag
from django.db.models import Count


class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'


def post_list(request, tag_slug=None):
    objects_list = Post.published.all()
    tag = None

    if  tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        objects_list = objects_list.filter(tags__in=[tag])

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
    context = {'page': page, 'posts': posts, 'tag': tag}
    return render(request, 'blog/post/list.html', context)


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post, 
                                status='published', 
                                publish__year=year, 
                                publish__month=month,
                                publish__day=day)
    comments = post.comments.filter(active=True)
    new_comment = None
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.save()
            return redirect(post.get_absolute_url())
    # GET or invalid form
    comment_form = CommentForm()
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]
    context = {'post': post, 
                'comments': comments, 
                'new_comment': new_comment,
                'comment_form': comment_form,
                'similar_posts': similar_posts}
    return render(request, 'blog/post/detail.html', context)

# email sending
def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False
    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            #what this???
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = '{} ({}) recommends you reading "{}"'.format(cd['name'], cd['email'], post.title)
            message = 'Read "{}" at {}\n\n{}\'s comments: {}'.format(post.title, post_url, cd['name'], cd['comments'])
            send_mail(subject, message, 'nikitamityushov@gmail.com', [cd['to'],])
            sent =  True
            context = {'post': post, 'form': form, 'sent': sent}
            return render(request, 'blog/post/share.html', context)
    # GET or invalid form
    form = EmailPostForm()
    context = {'post': post, 'form': form, 'sent': sent}
    return render(request, 'blog/post/share.html', context)
