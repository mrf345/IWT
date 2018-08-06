from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from django.contrib.auth import (
    login, authenticate, logout)
from django.core.paginator import Paginator
from django.db.models import Q
from IWT.core.forms import (
    AnyUserForm, MainUserForm, MainLoginForm,
    ChangePasswordForm, TextingForm, SearchForm)
from IWT.core.models import Texts
from gTTS.views import gTTs
from gtranslate.views import gTranslate
from gtranslate.templatetags.gtranslate import gtranslate
from re import compile, sub
from difflib import SequenceMatcher

# Default user stuff
title = 'IWT Interact With Text'
def_user = 'Anonymous'
def_lang = 'en'
try:
    User.objects.get(username=def_user)
except Exception:
    User.objects.create_user(
        def_user, None,
        def_user)


# Bypassing gtts and getranslate for previewing
bypassed_stuff = """
This is a brief <strong>demonstration</strong> of, an interactive text. 
You can interact with each word or sentence, by <b>hovering</b> over 
it with your mouse or <b>touching</b> it through your touch screen. You 
can translate and listen to <u>each word</u> or 
<u>sentence</u> <i>separately</i>."""
b_stuff_filtered = sub(compile('<.*?>'), '', bypassed_stuff)
b_stuff_filtered = b_stuff_filtered.replace(
    ',', '').replace('.', '').replace('\n', '')

def mode_gTTs(r, language, text):
    if not r.user.is_authenticated:
        global b_stuff_filtered
        s_stuff_filtered = b_stuff_filtered
        if not language.startswith('en'):
            s_stuff_filtered = gtranslate(
                src='en', dest=language.split('-')[0], 
                text=s_stuff_filtered)
        if text.replace(',', '').replace('.', '') not in s_stuff_filtered:
            if 1 > int(SequenceMatcher(a=s_stuff_filtered, b=text).ratio() * 10) and text.replace(',', '').replace('.', '') not in s_stuff_filtered:
                messages.add_message(r, messages.ERROR,
                'You can not interact with text, without authentication')
                return redirect('/')
    return gTTs(r, language=language, text=text)

def mode_gTranslate(r, src, dest, text):
    if not r.user.is_authenticated:
        global b_stuff_filtered
        if text.replace(',', '').replace('.', '') not in b_stuff_filtered:
            messages.add_message(r, messages.ERROR,
            'You can not interact with text, without authentication')
            return redirect('/')
    return gTranslate(r, src=src, dest=dest, text=text)



# Main index

def root(r):
    if 'lang' not in r.session:
        r.session['lang'] = def_lang
    if r.user.is_authenticated:
        return redirect('/texts')
    c = {'title': title, 'to_activate': '',
    'bypassed_stuff': mark_safe(bypassed_stuff),
    'form_any': AnyUserForm,
    'form_main': MainLoginForm,
    'form_register': MainUserForm}
    return render(r, 'index.html', c)

def lang_switch(r, lang, next):
    if next == 'root':
        next = '/'
    if lang not in ['en', 'fr', 'it', 'ar', 'es']:
        messages.add_message(
            r, messages.ERROR,
            'Language selected is not supported')
        return redirect(next)
    global def_lang
    def_lang = lang
    r.session['lang'] = def_lang
    messages.add_message(
    r, messages.INFO,
    'Default language switched successfully')
    return redirect(next)

# Authentications

def register_main(r):
    if r.method == 'POST':
        form = MainUserForm(r.POST)
        if form.is_valid():
            try:
                User.objects.create_user(
                    username=form.cleaned_data['username'],
                    email=form.cleaned_data['email'],
                    password=form.cleaned_data['password'])
                messages.add_message(
                    r, messages.INFO,
                    'User got registered, try to login')
                return redirect('/')
            except Exception:
                pass
    messages.add_message(
        r, messages.ERROR,
        'User already exists, or wrong values inserted')
    return redirect('/')

@login_required
def change_password(r):
    if r.user.username != def_user:
        form = ChangePasswordForm(r.POST)
        if form.is_valid():
            try:
                user = User.objects.get(
                    username=r.user.username)
                user.set_password(form.cleaned_data['password'])
                user.save()
                messages.add_message(
                    r, messages.INFO,
                    '%s password got updated' % r.user.username)
                login(r, authenticate(
                    r, username=r.user.username, 
                    password=form.cleaned_data['password']))
                return redirect('/texts')
            except Exception:
                pass
    messages.add_message(
        r, messages.ERROR,
        'Invalid change password attempt')
    return redirect('/')

def login_main(r):
    if r.method == 'POST':
        form = MainLoginForm(r.POST)
        if form.is_valid():
            try:
                user = User.objects.get(
                    email=form.cleaned_data['email'])
            except Exception:
                user = None
            if user is not None:
                auth = authenticate(
                    r, username=user.username,
                    password=form.cleaned_data['password'])
                if auth is not None:
                    login(r, auth)
                    messages.add_message(
                        r, messages.INFO,
                        'User logged in. Welcome back %s' % (
                            user.username))
                    return redirect('/texts')
    messages.add_message(
        r, messages.ERROR,
        'Invalid login attempt, wrong email or password')
    return redirect('/')


def login_any(r):
    if r.method == 'POST':
        form = AnyUserForm(r.POST)
        if form.is_valid():
            auth = authenticate(
                r, username=def_user, password=def_user)
            if auth is not None:
                login(r, auth)
                messages.add_message(
                    r, messages.INFO,
                    'User logged in as Anonymous')
                return redirect('/texts')
    messages.add_message(
        r, messages.ERROR,
        'Invalid login attempt')
    return redirect('/')

def logout_all(r):
    if r.user.is_authenticated:
        logout(r)
        messages.add_message(
            r, messages.INFO,
            'User got logged out')
        return redirect('/')
    messages.add_message(
        r, messages.ERROR,
        'User is not logged in !')
    return redirect('/')


# Core texts

@login_required
def texts(r):
    if 'lang' not in r.session:
        r.session['lang'] = def_lang
    all_texts = Texts.objects.all()
    paginator = Paginator(all_texts, 7)
    public_texts = len(
        Texts.objects.filter(
            user_id=User.objects.get(username=def_user).id))
    c = {'title': title + ' - Interactive texts',
    'to_activate': '#allTexts', 
    'form_password': ChangePasswordForm,
    'private_texts': len(all_texts) - public_texts,
    'public_texts': public_texts,
    'all_texts': len(all_texts),
    'form_search': SearchForm,
    'data': paginator.get_page(r.GET.get('page'))}
    return render(r, 'texts.html', c)

@login_required
def texts_sorted(r, sorting):
    if 'lang' not in r.session:
        r.session['lang'] = def_lang
    sorting_keys = ['oldest', 'newest', 'mostViewed', 
    'leastViewed', 'mostShared', 'leastShared']
    usernames = [str(user.id
    ) for user in User.objects.all()]
    if sorting not in sorting_keys and sorting not in usernames:
        messages.add_message(
            r, messages.ERROR,
            'Wrong sorting selected')
        return redirect('/texts')
    if sorting in usernames:
        if r.user.id != int(sorting):
            messages.add_message(
                r, messages.ERROR,
                'Your are not the author !')
            return redirect('/texts')
    if sorting == 'oldest':
        sorted_data = Texts.objects.order_by('date').reverse()
    elif sorting == 'newest':
        sorted_data = Texts.objects.order_by('date')
    elif sorting == 'mostViewed':
        sorted_data = Texts.objects.order_by('viewed').reverse()
    elif sorting == 'leastViewed':
        sorted_data = Texts.objects.order_by('viewed')
    elif sorting == 'mostShared':
        sorted_data = Texts.objects.order_by('shared').reverse()
    elif sorting == 'leastShared':
        sorted_data = Texts.objects.order_by('shared')
    elif sorting in usernames:
        sorted_data = Texts.objects.filter(
            user_id=User.objects.get(
                id=int(sorting)))
    all_texts = Texts.objects.all()
    public_texts = len(
    Texts.objects.filter(
        user_id=User.objects.get(username=def_user).id))
    paginator = Paginator(sorted_data, 7)
    c = {'title': title + ' - Sorted ' + sorting + ' texts' ,
    'to_activate': ('#yourTexts' 
    if sorting in usernames else '#sorting,#' + sorting),
    'form_password': ChangePasswordForm,
    'private_texts': len(all_texts) - public_texts,
    'public_texts': public_texts,
    'all_texts': len(all_texts),
    'form_search': SearchForm,
    'data': paginator.get_page(r.GET.get('page'))}
    return render(r, 'texts.html', c)

@login_required
def texting(r, text_id):
    if 'lang' not in r.session:
        r.session['lang'] = def_lang
    try:
        get_text_or_none = Texts.objects.get(id=text_id)
    except Exception:
        get_text_or_none = None
    if get_text_or_none is None:
        messages.add_message(
            r, messages.ERROR,
            'Selected interactive text not found')
        return redirect('/texts')
    if (get_text_or_none.user_id != r.user and 
    get_text_or_none.user_id.username != def_user):
        messages.add_message(
            r, messages.ERROR,
            'Trying to access a private text !')
        return redirect('/texts')
    get_text_or_none.viewed += 1
    get_text_or_none.save()
    form = TextingForm
    c = {'title': title + ' - Previewing ' + get_text_or_none.title,
    'to_activate': '', 'form_password': ChangePasswordForm,
    'form_search': SearchForm,
    'form': form, 'data': get_text_or_none}
    return render(r, 'texting.html', c)

@login_required
def adding_text(r):
    if 'lang' not in r.session:
        r.session['lang'] = def_lang
    form = TextingForm
    if r.method == 'POST':
        form = form(r.POST)
        if form.is_valid():
            text = Texts(
                text=form.cleaned_data['text'],
                title=form.cleaned_data['title'],
                user_id=User.objects.get(
                username=r.user.username))
            text.save()
            messages.add_message(
                r, messages.INFO,
                'New text got added')
            return redirect('/texting/' + str(text.id))
        else:
            messages.add_message(
                r, messages.ERROR,
                'Wrong data entered')
    c = {'title': title + ' - Adding text',
    'form_search': SearchForm,
    'to_activate': '#addText', 'form': form}
    return render(r, 'texting_add.html', c)

@login_required
def editing_text(r, text_id):
    if 'lang' not in r.session:
        r.session['lang'] = def_lang
    try:
        text = Texts.objects.get(id=text_id)
    except Exception:
        text = None
    if text is None:
        messages.add_message(r, messages.ERROR,
        'Text not found or something went wrong')
        return redirect('/texts')
    form = TextingForm
    if r.method == 'POST':
        form = form(r.POST)
        if form.is_valid():
            text.title = form.cleaned_data['title']
            text.text = form.cleaned_data['text']
            text.save()
            messages.add_message(r, messages.INFO,
            'Text got updated and modified')
            return redirect('/texting/' + str(text_id))
        else:
            messages.add_message(r, messages.ERROR,
            'Update data entered is invalid')
    else:
        form = form(initial={'title': text.title})
    c = {'title': title + ' - Updating text',
    'form_search': SearchForm,
    'to_activate': '', 'form': form, 'text': text.text}
    return render(r, 'texting_add.html', c)

@login_required
def removing_text(r, text_id):
    if 'lang' not in r.session:
        r.session['lang'] = def_lang
    try:
        text = Texts.objects.get(id=text_id)
    except Exception:
        text = None
    if text is not None:
        if r.user == text.user_id and r.user.username != def_user:
            text.delete()
            messages.add_message(r, messages.INFO,
            'Text got deleted for good')
        else:
            messages.add_message(r, messages.ERROR,
            'User is not allowed to delete this text !')
    else:
        messages.add_message(r, messages.ERROR,
        'Text not found or something went wrong')
    return redirect('/texts')

@login_required
def share_text(r, share, text_id):
    try:
        text = Texts.objects.get(id=text_id)
    except Exception:
        text = None
    links = {'facebook': 'https://www.facebook.com/sharer.php?u=',
    'google+': 'https://plus.google.com/share?url=',
    'linkedin': 'http://www.linkedin.com/shareArticle?mini=true&amp;url=',
    'twitter': 'https://twitter.com/share?url='}
    if text is None or share not in links.keys():
        messages.add_message(
            r, messages.ERROR,
            'Text not found or something went wrong')
        return redirect('/texts')
    text.shared += 1
    text.save()
    return redirect("%s%s" % (
        links.get(share),
        r.build_absolute_uri().replace(
            'share_text/' + share + '/' + str(
                text_id), '') + 'texting/' + str(
                    text_id)), target='_blank')

@login_required
def search_text(r):
    if r.method == 'POST':
        form = SearchForm(r.POST)
        if form.is_valid():
            try:
                text = Texts.objects.filter(Q(
                    title__contains=form.cleaned_data['text']
                    ) | Q(
                        text__contains=form.cleaned_data['text']))
            except Exception:
                text = None
            if text is None:
                messages.add_message(
                    r, messages.ERROR,
                    'Your search has no results, unfortunately')
                return redirect('/texts')
            if len(text) == 0:
                messages.add_message(
                r, messages.ERROR,
                'Your search has no results, unfortunately')
            all_texts = Texts.objects.all()
            paginator = Paginator(text, 7)
            public_texts = len(
                Texts.objects.filter(
                    user_id=User.objects.get(username=def_user).id))
            c = {'title': title + ' - Interactive texts',
            'to_activate': '#allTexts', 
            'form_password': ChangePasswordForm,
            'private_texts': len(all_texts) - public_texts,
            'public_texts': public_texts,
            'all_texts': len(all_texts),
            'form_search': form,
            'data': paginator.get_page(r.GET.get('page'))}
            return render(r, 'texts.html', c)
    messages.add_message(
        r, messages.ERROR,
        'Invalid search values')
    return redirect('/texts')


# Management

@login_required
def delete(r):
    if r.user.is_authenticated:
        if r.user.username != def_user:
            try:
                user = User.objects.get(
                    username=r.user.username)
                # Add delete texts
                user.delete()
                messages.add_message(
                    r, messages.INFO,
                    '%s got deleted, thanks for trying IWT' % (
                        r.user.username))
                return redirect('/')     
            except Exception:
                pass
    messages.add_message(
        r, messages.ERROR,
        'Invalid delete account attempt')
    return redirect('/')

# Redirections and Errors

def no_js(r):
    if 'lang' not in r.session:
        r.session['lang'] = def_lang
    if r.user.is_authenticated():
        logout(r)
    messages.add_message(
        r, messages.ERROR,
        'You can not processed without JavaScript.')
    c = {'title': title + ' - NoScript discovered',
    'to_activate': ''}
    return render(r, 'nojs.html', c)

def not_logged(r):
    messages.add_message(
        r, messages.ERROR,
        'Accessing that route requires authentication')
    return redirect('/')

def wrong_route(r):
    messages.add_message(
        r, messages.ERROR, 
        'Wrong path, or something went wrong.')
    return redirect('/')

def csrf_failure(request, reason=""):
    messages.add_message(
        request, messages.ERROR, 
        'Outdated, request try to submit again.')
    return redirect('/')