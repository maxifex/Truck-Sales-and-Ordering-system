from django.conf.urls import patterns, include, url
from orderSystem import views

urlpatterns = patterns('',

    url(r'^$', views.UserAccountView, name='accountView'),
    url(r'^logout$', views.userLogoutView, name='logoutView'),

    #Homepage/Dashboard
    url(r'^home', views.index, name='home'),
    url(r'^account$', views.UserAccountView, name='accountView'),
    url(r'^account_bg$', views.UserAccount, name='account_bg'),

    url(r'^dashboard$', views.dashboardView, name='dashboardView'),
    url(r'^dashboard_gb$', views.dashboardView, name='dashboard_gb'),

    url(r'^profile$', views.profileView, name='profileView'),
    url(r'^profileSave$', views.profileSave, name='profileSave'),

    url(r'^staff$', views.staffView, name='staffView'),
    url(r'^staffSave$', views.staffSave, name='staffSave'),

    url(r'^client$', views.clientView, name='clientView'),
    url(r'^clientSave$', views.clientSave, name='clientSave'),
    url(r'^clientList$', views.clientList, name='clientList'),

    url(r'^orderform$', views.orderFormView, name='orderFormView'),
    url(r'^orderform(?P<order_id>[0-9]+)/$', views.orderFormView, name='orderFormView'),
    url(r'^order$', views.orderView, name='orderView'),
    url(r'^orderSave$', views.orderSave, name='orderSave'),


    url(r'^proforma$', views.proformaView, name='proformaView'),
    url(r'^proforma(?P<order_id>[0-9]+)/$', views.proformaView, name='proformaView'),
    url(r'^proformapdf$', views.proformaPDF, name='proformaPDF'),
    url(r'^proformapdf(?P<order_id>[0-9]+)/$', views.proformaPDF, name='proformaPDF'),

    url(r'^qsf$', views.qsfView, name='qsfView'),
    url(r'^qsf(?P<order_id>[0-9]+)/$', views.qsfView, name='qsfView'),
    url(r'^qsfpdf$', views.qsfPDF, name='qsfPDF'),
    url(r'^qsfpdf(?P<order_id>[0-9]+)/$', views.qsfPDF, name='qsfPDF'),

    url(r'^calculation$', views.calculationView, name='calculationView'),
    url(r'^calculation(?P<order_id>[0-9]+)/$', views.calculationView, name='calculationView'),

    url(r'^mof$', views.mofView, name='mofView'),
    url(r'^mof(?P<order_id>[0-9]+)/$', views.mofView, name='mofView'),
    url(r'^mofpdf$', views.mofPDF, name='mofPDF'),
    url(r'^mofpdf(?P<order_id>[0-9]+)/$', views.mofPDF, name='mofPDF'),


)