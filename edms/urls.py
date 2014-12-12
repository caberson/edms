from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'edms.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^student/', include('student.urls')),

    url(r'^admin/', include(admin.site.urls)),
)
