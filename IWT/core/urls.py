from django.urls import path
from django.conf.urls import url
# Views
from IWT.core.views import (
    root, wrong_route, texts, texts_sorted,
    no_js, not_logged, texting, login_any,
    logout_all, login_main, register_main,
    change_password, delete, adding_text,
    editing_text, removing_text, share_text,
    search_text, mode_gTTs, mode_gTranslate)

urlpatterns = [path('nojs', no_js),
path('not_logged', not_logged),
path('texts', texts),
path('texts_sorted/<sorting>', texts_sorted),
path('texting/<int:text_id>', texting),
path('adding_text', adding_text),
path('updating_text/<int:text_id>', editing_text),
path('removing_text/<int:text_id>', removing_text),
path('share_text/<share>/<int:text_id>', share_text),
path('search_text', search_text),
path('login_any', login_any),
path('login_main', login_main),
path('register_main', register_main),
path('logout_all', logout_all),
path('change_password', change_password),
path('delete', delete),
path('gtts/<language>/<text>', mode_gTTs),
path('tran/<src>/<dest>/<text>', mode_gTranslate),
path('', root),
url('', wrong_route)]

