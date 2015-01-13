from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseServerError
from django.contrib.auth import authenticate, login, logout

from django.shortcuts import render, redirect
from django.http import HttpResponse
from orderSystem.models import Employee, User, Client, Country, DeliveryTime, SpecialDiscount, Discount, Currency, DutyType, TruckAge, PaymentTerm, Order, CustomConfiguration, Depreciation, CustomsRate
from django.db.models import Count, Min, Sum, Avg, Max
from django.template import RequestContext, loader
from django.views.generic import ListView
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseServerError
from datetime import date, datetime, timedelta
from django.contrib.auth import authenticate, login, logout
from django.core.urlresolvers import reverse
from xlwt import Workbook, easyxf
# from django.contrib.auth.models import User
from validate_email import validate_email
from django.db.models import Count, Q
from django.contrib.auth.hashers import make_password
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.conf import settings
import re, operator
import calendar
from django.db import transaction
from reportlab.pdfgen import canvas
import time
from datetime import date, datetime

import json
import StringIO
import cStringIO as StringIO
import ho.pisa as pisa
from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse
from cgi import escape

permissions = {'Administrator' : 32, 'Sales Representative' : 16}



def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    context = Context(context_dict)
    html  = template.render(context)
    result = StringIO.StringIO()

    pdf = pisa.pisaDocument(StringIO.StringIO(html.encode("utf-8")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), mimetype='application/pdf')
    return HttpResponse('We had some errors<pre>%s</pre>' % escape(html))

def fetch_resources(uri, rel):
    import os.path
    from django.conf import settings

    path = os.path.join(
            settings.STATIC_ROOT,
            uri.replace(settings.STATIC_URL, ""))
    return path

def render_to_pdf2(template_src, context_dict):
    """Function to render html template into a pdf file"""
    template = get_template(template_src)
    context = Context(context_dict)
    html  = template.render(context)
    result = StringIO.StringIO()

    pdf = pisa.pisaDocument(StringIO.StringIO(html.encode("UTF-8")),
                                            dest=result,
                                            encoding='UTF-8',
                                            link_callback=fetch_resources)
    if not pdf.err:
        response = HttpResponse(result.getvalue(), mimetype='application/pdf')

        return response

    return HttpResponse('We had some errors<pre>%s</pre>' % escape(html))



def index(request):
    return render(request, 'index.html', {})

def dashboardView(request):
    context = {}
    ckwargs = {}
    pkwargs = {}
    skwargs = {}

    if request.user.is_authenticated():

        return render(request, 'dashboard.html', context)
    else:
        return render(request, 'login.html', context)

def userLogoutView(request):
    logout(request)
    return render(request, 'login.html', {})

def UserAccountView(request):
    context = {}
    if request.user.is_authenticated():
        return userLogoutView(request)
    else:
        return render(request, 'login.html', context)

def UserAccount(request):

    if request.POST and not request.user.is_authenticated():
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if not hasattr(user, 'employee'):
                response_data = {'is_valid':False, 'data':'User account improperly setup. Contact sys Admin'}
                return HttpResponse(json.dumps(response_data), mimetype="application/json")

            if user.is_active:
                login(request, user)
                redirect_url = reverse('man:dashboardView')

                response_data = {'is_valid':True, 'data':'success', 'redirect_url': redirect_url}
                return HttpResponse(json.dumps(response_data), mimetype="application/json")
                # Redirect to a success page.
            else:
                # Return a 'disabled account' error message
                response_data = {'is_valid':False, 'data':'Account has been Disabled'}
                return HttpResponse(json.dumps(response_data), mimetype="application/json")
        else:
            # Return an 'invalid login' error message.
            response_data = {'is_valid':False, 'data':'Invalid Login details'}
            return HttpResponse(json.dumps(response_data), mimetype="application/json")
    else:
        # Return an 'invalid login' error message.
        response_data = {'is_valid' : False, 'data':'Post parameters not available'}
        return HttpResponse(json.dumps(response_data), mimetype="application/json")

@transaction.atomic
def profileSave(request):

    if request.POST and request.user.is_authenticated():
        is_valid = False
        avatar_url = False
        message = "success"

        if request.POST['edit-type'] == 'info':
            if ( request.POST['profile_email']):
                is_email_valid = validate_email(request.POST['profile_email'])
            if not (request.POST['profile_username']):
                message = "Fill in username"
            if ( not (request.POST['profile_firstname']) or not request.POST['profile_lastname']):
                message = "Fill in First name and Last name"
            elif ( not (request.POST['profile_phone']) or not request.POST['profile_phone'].isdigit()):
                message = "Mobile number invalid"
            elif ( request.POST['profile_email'] and not is_email_valid):
                message = "Please provide a valid email address"
            elif not ('profile_phone' in request.POST) or not validPhoneNumber(request.POST['profile_phone']):
                message = "Mobile number invalid. should be of the format 23324XXXXXXX"

            # Check if customer username already exists
            if(request.user.username != request.POST['profile_username']):
                user = User.objects.all().filter(username = request.POST['profile_username'])
                if(user):
                    message = "Username already exists. Please Try another name"

            # Check if phone number already exists
            if(not hasattr(request.user, 'employee') or request.user.employee.phone_number != request.POST['profile_phone']):
                user_phone = Employee.objects.all().filter(phone_number = request.POST['profile_phone'], status='A')
                if(user_phone):
                    message = "Phone number already in user by another employee"

            if(message == "success"):
                user = User.objects.get(pk=request.user.id)
                user.username = request.POST['profile_username']
                user.first_name = request.POST['profile_firstname']
                user.last_name = request.POST['profile_lastname']
                user.email = request.POST['profile_email']
                user.save()

                if(user):
                    if(hasattr(user, 'employee') and user.employee):
                        user.employee.phone_number = request.POST['profile_phone']
                        # user.employee.gender = request.POST['profile_gender']
                        user.employee.save()
                        employee = user.employee
                    else:
                        employee = Employee.objects.create(phone_number=request.POST['profile_phone'], user=user)

                    if employee:
                        message = "<b>Congratulations!</b> Profile has been updated successfully"
                        is_valid = True
                else:
                    message = "Could not update profile information. Please check with system admin"
                    message = "<b>Oops..</b>" + message
            else:
                message = "<b>Oops..</b>" + message

        if request.POST['edit-type'] == 'password':
            if ( not request.POST['profile_password'] or  not request.POST['profile_new_passord'] or  not request.POST['profile_confirm_password']):
                message = "Please provide a the Old, New and Confirmation password"
            elif not request.user.check_password(request.POST['profile_password']):
            #now check to see if the old password is correct
                message = "Existing password is incorrect"
                message = "<b>Oops..</b>" + message
            elif (request.POST['profile_new_passord'] != request.POST['profile_confirm_password']):
                message = "New password and Confirmation passwords do not match"
            else:
                user = User.objects.get(pk=request.user.id)
                if(user):
                    user.set_password(request.POST['profile_new_passord'])
                    user.save()
                    message = "<b>Congratulations!</b> password has been updated successfully"
                    is_valid = True
                else:
                    message = "<b>Congratulations!</b> password has been updated successfully"
                    message = "<b>Oops..</b>" + message

        if 'upload_avatar' in request.FILES:
            upload_avatar = request.FILES['upload_avatar']
            user = User.objects.get(pk=request.user.id)
            if(hasattr(user, 'employee') and user.employee):
                user.employee.avatar.save(upload_avatar.name,upload_avatar)
                avatar_url = user.employee.avatar.url
                message = "<b>Congratulations!</b> image has been saved successfully"
                is_valid = True
            else:
                message = "<b>Oops!</b> message could not be saved successfully. Please make sure profile details are complete"

        if(message == "success"):
            message = "<b>Oops!</b> no action was perform"


        response_data = {'is_valid': is_valid, 'data':message, 'avatar_url':avatar_url}
        return HttpResponse(json.dumps(response_data), mimetype="application/json")

    # elif request.POST and not request.user.is_authenticated():
    #     response_data = {'is_valid':False, 'data':'Please refresh your page and try again'}
    #     return HttpResponse(json.dumps(response_data), mimetype="application/json")

    elif request.user.is_authenticated():
        context = {'profile': request.user}
        return render(request, 'atom/profile-edit.html', context)
    else:
        return render(request, 'atom/login.html', {})

def profileView(request):
    if request.user.is_authenticated():
        context = {'profile': request.user}
        return render(request, 'profile.html', context)
    else:
        return render(request, 'login.html', {})

@transaction.atomic
def staffSave(request):
    context = {}

    if request.POST and request.user.is_authenticated():

        is_create = True
        kwargs = {}
        kwargs_username = {}
        is_email_valid = True
        message = ""
        staff = None
        if('staff_email' in request.POST and not request.POST["staff_email"] == ""):
            is_email_valid = validate_email(request.POST['staff_email'])

        if 'item_id' in request.POST and request.POST['item_id'].isdigit():
            is_create = False
            id = request.POST['item_id']
            user_id = request.POST['user_id']
            kwargs['id'] = id
            kwargs_username['id'] = request.POST['user_id']

            if('status' in request.POST and request.POST['status'] == 'D'):
                #update the check details with new records
                User.objects.filter(pk=user_id).update(is_active = 0)
                Employee.objects.filter(pk=id).update(status = request.POST['status'])
                response_data = {'is_valid':True, 'data':'Item successfully deleted'}
                return HttpResponse(json.dumps(response_data), mimetype="application/json")

        elif 'item_id' in request.POST and not request.POST['item_id'].isdigit():
            message = "Update to an invalid item"

        is_valid = False
        message = "success"
        if request.user.employee.position < permissions['Administrator']:
            message = "You are unauthorised to perform this action"
        elif ( not ('username' in request.POST)):
            message = "Please provide username"
        elif ( not ('firstname' in request.POST) or not ('lastname' in request.POST)):
            message = "Fill in First name and Last name"
        elif not ('phone' in request.POST) or not validPhoneNumber(request.POST['phone']):
            message = "Mobile number invalid. should be of the format 23324XXXXXXX"
        elif (not is_email_valid):
            message = "Please provide a valid email address"
        elif ( not 'password' in request.POST or  not 'cpassword' in request.POST) and is_create:
            message = "Please provide a password and a confirmation"
        elif not (request.POST['password'] == request.POST['cpassword']):
            message = "Password and confirmation do not match"
        elif ( not 'accountType' in request.POST or not request.POST['accountType']):
            message = "Please select a user account type"
        elif not is_create and int(user_id) == request.user.id and not(permissions[request.POST['accountType']] == request.user.employee.position):
            message = "You are not allowed to change your role. This is so that your don't lock yourself out"

        # Check if customer username already exists
        user = User.objects.all().filter(username = request.POST['username']).exclude(**kwargs_username)
        if(user):
            message = "Username already exists"

        # Check if phone number already exists system wide
        user_phone = Employee.objects.all().filter(Q(phone_number = request.POST['phone']), status='A').exclude(**kwargs)

        if(user_phone):
            message = "Phone number is already in use by another staff"

        if(message == "success"):
            is_staff = 1
            role = permissions[request.POST['accountType']]

            if is_create:
                user = User.objects.create(username=request.POST['username'], first_name=request.POST['firstname'], last_name=request.POST['lastname'],
                                           password=make_password(request.POST['password']), email=request.POST['staff_email'], date_joined=datetime.now(), is_active=1, is_staff=is_staff)
            else:
                #update the cash details with new records
                user = User.objects.filter(pk=user_id).update(username=request.POST['username'], first_name=request.POST['firstname'], last_name=request.POST['lastname'],
                                           email=request.POST['staff_email'], is_active=1, is_staff=is_staff)
                if 'password' in request.POST and request.POST['password']:
                    user = User.objects.filter(pk=user_id).update(password=make_password(request.POST['password']))


            if(user):
                if is_create:
                    staff = Employee.objects.create(phone_number=request.POST['phone'], user=user, position = role)
                else:
                    #update the cash details with new records
                    staff = Employee.objects.filter(pk=id).update(phone_number=request.POST['phone'], position = role)

                if staff:
                    message = "<b>Congratulations!</b> New staff account created successfully" if is_create else "<b>Congratulations!</b> Staff record has been updated"
                    is_valid = True

                    if isinstance(staff, Employee):
                        staff = staff.id

                    staff = Employee.objects.get(pk=staff)
                    if 'upload_signature' in request.FILES:
                        upload_avatar = request.FILES['upload_signature']
                        user = staff.user
                        if(hasattr(user, 'employee') and user.employee):
                            user.employee.signature.save(upload_avatar.name,upload_avatar)
                            avatar_url = user.employee.signature.url

                    if(message == "success"):
                        message = "<b>Oops!</b> no action was performed"

                else:
                    message = "Staff account could not be created. Please check with system admin"
            else:
                message = "New staff could not be created. Please check with system admin"
                message = "<b>Oops..</b>" + message
        else:
            message = "<b>Oops..</b>" + message


        response_data = {'is_valid':is_valid, 'data':message}
        return HttpResponse(json.dumps(response_data), mimetype="application/json")

    elif request.POST and not request.user.is_authenticated():
        response_data = {'is_valid':False, 'data':'Please refresh your page and try again'}
        return HttpResponse(json.dumps(response_data), mimetype="application/json")

    elif request.user.is_authenticated():

        if not request.user.employee.position >= permissions['Administrator']:
            return dashboardView(request)

        return render(request, 'atom/staff-register.html', {'permissions' : permissions})
    else:
        return render(request, 'atom/login.html', context)

def staffView(request):
    if request.user.is_authenticated():
        staff = Employee.objects.all().filter(status='A').order_by('user__first_name', 'user__last_name')
        context = {'staff': staff, 'permissions':permissions}
        return render(request, 'staff.html', context)
    else:
        return render(request, 'login.html', {})

def clientView_old(request):
    if request.user.is_authenticated():
        countries = Country.objects.all().filter(status='A').order_by('name')
        client = Client.objects.all().filter(status='A').order_by('-created_date')[:100]
        context = {'client': client, 'permissions':permissions, 'countries' : countries}
        return render(request, 'client.html', context)
    else:
        return render(request, 'login.html', {})

def clientView(request):
    if request.user.is_authenticated():

        dateFilter = 'created_date__range'
        kwargs = {'status' : 'A'}

        clientSelector = '0'
        employeeSelector = '0'
        countrySelector =""
        clientNumber = ""
        clientSelector = ""

        if( 'employeeFilter' in request.GET and request.GET['employeeFilter'] and request.GET['employeeFilter'] !='0'):
            employeeSelector = request.GET['employeeFilter']
            kwargs['created_by'] = request.GET['employeeFilter']

        if( 'countryFilter' in request.GET and request.GET['countryFilter'] and request.GET['countryFilter'] !='0'):
            countrySelector = request.GET['countryFilter']
            kwargs['country'] = request.GET['countryFilter']

        if( 'clientFilter' in request.GET and request.GET['clientFilter'] and 'clientNumber' in request.GET and request.GET['clientNumber']):
            clientSelector = request.GET['clientFilter']
            clientNumber = request.GET['clientNumber']
            kwargs['id'] = request.GET['clientFilter']

        #Change Date to allowed date format
        if 'postedFrom' in request.GET and request.GET['postedFrom'] and 'postedTo' in request.GET and request.GET['postedTo']:
            postedFrom = datetime.strptime(request.GET['postedFrom'], '%m/%d/%Y')
            postedTo = datetime.strptime(request.GET['postedTo'], '%m/%d/%Y')# + timedelta(days=1)
            kwargs[dateFilter] = [postedFrom, postedTo]
            client = Client.objects.all().filter(**kwargs).order_by('-created_date')[:100]
            # orders = Order.objects.filter(**kwargs).order_by('-order_date')
            postedFrom = postedFrom.strftime('%m/%d/%Y')
            postedTo = postedTo.strftime('%m/%d/%Y')
        else:
            lastWeek = datetime.now() + timedelta(days=-50)
            postedFrom = lastWeek.date()
            postedTo =date.today() + timedelta(days=1)
            kwargs[dateFilter] = [postedFrom, postedTo]
            client = Client.objects.all().filter(**kwargs).order_by('-created_date')[:100]
            orders = Order.objects.filter(**kwargs).order_by('-order_date')
            postedFrom = postedFrom.strftime('%m/%d/%Y')
            postedTo = postedTo.strftime('%m/%d/%Y')


        country = Country.objects.all().filter(status='A').order_by('name')
        employee = Employee.objects.all().filter(status='A').order_by('-user__last_name')


        context = {'postedFrom': postedFrom, 'postedTo': postedTo, 'employeeFilter':employeeSelector, 'clientFilter':clientSelector, 'clientNumber':clientNumber,
                   'employee':employee, 'country' : country, 'client': client, 'permissions':permissions, 'countryFilter':countrySelector}

        return render(request, 'client.html', context)
    else:
        return render(request, 'login.html', {})

def clientList(request):

    if request.user.is_authenticated():
        search_query = request.GET['term']
        qset = Q()
        for term in search_query.split():
            qset |= Q(company_name__icontains=term)

        if __strType(request.GET['term']) == 'int':
            qset |= Q(client_id__contains=term)


        client = Client.objects.filter(qset, status='A').values('client_id', 'id', 'company_name', 'first_name', 'last_name', 'email', 'alt_email', 'business_phone', 'address', 'city', 'country__name').order_by('company_name')
        response_data = []
        for cust in client:
            response_data.append({ 'label': cust['company_name']+' ('+cust['client_id']+')', 'value': cust['client_id'], 'id':cust['id'], 'address':cust['address']
                , 'contact_person':cust['first_name'] +' '+cust['last_name'], 'email':cust['email'], 'business_phone':cust['business_phone'], 'city':cust['city'], 'country':cust['country__name']})


        return HttpResponse(json.dumps(response_data), mimetype="application/json")

    else:
        response_data = {'data':"no data; Login First"}
        return HttpResponse(json.dumps(response_data), mimetype="application/json")

@transaction.atomic
def clientSave(request):
    context = {}

    if request.POST and request.user.is_authenticated():

        message = "success"
        is_valid = False
        is_create = True
        is_email_valid = True
        is_altemail_valid = True
        kwargs = {}
        client = None
        if ( 'client_email' in request.POST and request.POST['client_email']):
            is_email_valid = validate_email(request.POST['client_email'])

        if ( 'alt_email' in request.POST and request.POST['alt_email']):
            is_altemail_valid = validate_email(request.POST['alt_email'])

        if 'item_id' in request.POST and request.POST['item_id'].isdigit():
            is_create = False
            id = request.POST['item_id']
            kwargs['id'] = id
            if('status' in request.POST and request.POST['status'] == 'D'):
                #update the check details with new records
                Client.objects.filter(pk=id).update(status = request.POST['status'], modified_date = datetime.now(), modified_by=request.user)
                response_data = {'is_valid':True, 'data':'Item successfully deleted'}
                return HttpResponse(json.dumps(response_data), mimetype="application/json")
        elif 'item_id' in request.POST and request.POST['item_id'] and not request.POST['item_id'].isdigit():
            message = "Update to an invalid item"
        if request.user.employee.position < permissions['Sales Representative']:
            message = "You are unauthorised to perform this action"
        elif not (request.POST['company']):
            message = "Fill in the Company name of the client"
        elif ( not (request.POST['contact'])):
            message = "Fill in name of Contact Person"
        elif ( not (request.POST['business_phone']) or not validPhoneNumber(request.POST['business_phone'])):
            message = "Business phone is invalid. should be of the format 23324XXXXXXX"
        elif ( 'mobile_phone' in request.POST and request.POST['mobile_phone'] and not validPhoneNumber(request.POST['mobile_phone'])):
            message = "Alternate Mobile Number is invalid. Should be of the format 23324XXXXXXX"
        elif not is_email_valid:
            message = "Please enter a valid email address"
        elif not is_altemail_valid:
            message = "Please enter a valid alternative email address"


        if(message == "success"):
            mobile_phone = request.POST['mobile_phone'] if 'mobile_phone' in request.POST and request.POST['mobile_phone'] and validPhoneNumber(request.POST['mobile_phone']) else ''
            fax = request.POST['fax'] if 'fax' in request.POST and request.POST['fax'] and validPhoneNumber(request.POST['fax']) else ''
            city = request.POST['city'] if 'city' in request.POST and request.POST['city'] else ''
            address = request.POST['address'] if 'address' in request.POST and request.POST['address'] else ''
            contact = request.POST['contact'].strip().rsplit(' ', 1)
            firstName = contact[0]
            lastName = ''
            if len(contact)>1:
                lastName = contact[1]


            alt_email = request.POST['alt_email'] if 'alt_email' in request.POST and request.POST['alt_email'] else ''
            if is_create:
                creator = request.user

                lastestClientID = Client.objects.aggregate(max = Max('client_id'))
                client_id = int(lastestClientID['max']) + 3

                client = Client.objects.create(client_id=client_id, first_name=firstName, last_name=lastName,country_id = request.POST['country'],
                                email=request.POST['client_email'],alt_email= alt_email, business_phone=request.POST['business_phone'], mobile_phone=mobile_phone,
                                company_name = request.POST['company'], fax = fax, address = address, city = city,
                                created_date=datetime.now(), created_by=creator, modified_date = datetime.now(), modified_by=request.user)


            else:
                #update the customer details with new records
                client = Client.objects.filter(pk=id).update(first_name=firstName, last_name=lastName,country = request.POST['country'],
                                email=request.POST['client_email'], alt_email= alt_email, business_phone=request.POST['business_phone'],
                                company_name = request.POST['company'], fax = fax, address = address, city = city,
                                mobile_phone=mobile_phone, modified_date = datetime.now(), modified_by=request.user)

            if(client):
                message = "<b>Congratulations!</b> Client account created successfully"
                is_valid = True
            else:
                message = "New Client's could not be created. Please check with system administrator"
                message = "<b>Oops..</b>" + message
        else:
            message = "<b>Oops..</b>" + message


        client_id = client.client_id if client and is_create else 0
        response_data = {'is_valid':is_valid, 'data':message, 'client_id':client_id}
        return HttpResponse(json.dumps(response_data), mimetype="application/json")

    elif request.POST and not request.user.is_authenticated():
        response_data = {'is_valid':False, 'data':'Please refresh your page and try again'}
        return HttpResponse(json.dumps(response_data), mimetype="application/json")

def validPhoneNumber(number):
    if len(number) >5 and len(number)<20 and number.isdigit():
        return True
    else:
        return False


def orderView(request):
    if request.user.is_authenticated():

        dateFilter = 'created_date__range'
        kwargs = {'status' : 'A'}

        clientSelector = '0'
        employeeSelector = '0'
        statusSelector =""
        clientNumber = ""
        clientSelector = ""

        if( 'employeeFilter' in request.GET and request.GET['employeeFilter'] and request.GET['employeeFilter'] !='0'):
            employeeSelector = request.GET['employeeFilter']
            kwargs['created_by'] = request.GET['employeeFilter']

        if( 'statusFilter' in request.GET and request.GET['statusFilter'] and request.GET['statusFilter'] !='0'):
            statusSelector = request.GET['statusFilter']
            kwargs['order_status'] = request.GET['statusFilter']

        if( 'clientFilter' in request.GET and request.GET['clientFilter'] and 'clientNumber' in request.GET and request.GET['clientNumber']):
            clientSelector = request.GET['clientFilter']
            clientNumber = request.GET['clientNumber']
            kwargs['client'] = request.GET['clientFilter']


        #Change Date to allowed date format
        if 'postedFrom' in request.GET and request.GET['postedFrom'] and 'postedTo' in request.GET and request.GET['postedTo']:
            postedFrom = datetime.strptime(request.GET['postedFrom'], '%m/%d/%Y')
            postedTo = datetime.strptime(request.GET['postedTo'], '%m/%d/%Y')# + timedelta(days=1)
            # postedTo = postedTo.strftime('%Y-%m-%d')
            kwargs[dateFilter] = [postedFrom, postedTo]
            orders = Order.objects.filter(**kwargs).order_by('-order_date')
            postedFrom = postedFrom.strftime('%m/%d/%Y')
            postedTo = postedTo.strftime('%m/%d/%Y')
        else:
            lastWeek = datetime.now() + timedelta(days=-50)
            postedFrom = lastWeek.date()
            postedTo =date.today() + timedelta(days=1)
            kwargs[dateFilter] = [postedFrom, postedTo]
            orders = Order.objects.filter(**kwargs).order_by('-order_date')
            postedFrom = postedFrom.strftime('%m/%d/%Y')
            postedTo = postedTo.strftime('%m/%d/%Y')


        country = Country.objects.all().filter(status='A').order_by('name')
        deliverytime = DeliveryTime.objects.all().filter(status='A').order_by('name')
        discount = Discount.objects.all().filter(status='A').order_by('percent')
        specialdiscount = SpecialDiscount.objects.all().filter(status='A').order_by('percent')
        currency = Currency.objects.all().filter(status='A', is_default='Y')
        dutytype = DutyType.objects.all().filter(status='A').order_by('name')
        truckage = TruckAge.objects.all().filter(status='A').order_by('year')
        paymentterm = PaymentTerm.objects.all().filter(status='A').order_by('duration')
        employee = Employee.objects.all().filter(status='A').order_by('-user__last_name')

        # client = Client.objects.all().filter(status='A').order_by('-created_date')
        # context = {'sms': sms, 'users': users, 'postedFrom': postedFrom.strftime('%d-%m-%Y'),
        #            'postedTo': postedTo.strftime('%d-%m-%Y'), 'userFilter':userSelector, 'typeFilter':typeSelector}
        #'postedTo': postedTo.strftime('%d-%m-%Y'),

        context = {'postedFrom': postedFrom, 'postedTo': postedTo, 'employeeFilter':employeeSelector, 'statusFilter':statusSelector, 'clientFilter':clientSelector, 'clientNumber':clientNumber,
                   'orders': orders, 'employee':employee, 'country' : country, 'deliverytime': deliverytime, 'discount': discount,
                   'specialdiscount': specialdiscount, 'currency': currency, 'dutytype': dutytype, 'truckage': truckage, 'paymentterm': paymentterm}

        return render(request, 'order2.html', context)
    else:
        return render(request, 'login.html', {})


def orderFormView(request):
    if request.user.is_authenticated():

        country = Country.objects.all().filter(status='A').order_by('name')
        deliverytime = DeliveryTime.objects.all().filter(status='A').order_by('name')
        discount = Discount.objects.all().filter(status='A').order_by('percent')
        specialdiscount = SpecialDiscount.objects.all().filter(status='A').order_by('percent')
        currency = Currency.objects.all().filter(status='A', is_default='Y')
        dutytype = DutyType.objects.all().filter(status='A').order_by('name')
        truckage = TruckAge.objects.all().filter(status='A').order_by('year')
        paymentterm = PaymentTerm.objects.all().filter(status='A').order_by('duration')

        order = None
        if( 'order_id' in request.GET and request.GET['order_id']):
            order = Order.objects.get(pk=request.GET['order_id'])


        # client = Client.objects.all().filter(status='A').order_by('-created_date')

        context = {'order':order, 'country' : country, 'deliverytime': deliverytime, 'discount': discount, 'specialdiscount': specialdiscount, 'currency': currency,
                   'dutytype': dutytype, 'truckage': truckage, 'paymentterm': paymentterm}
        return render(request, 'orderForm.html', context)
    else:
        return render(request, 'login.html', {})

@transaction.atomic
def orderSave(request):
    context = {}

    if request.POST and request.user.is_authenticated():

        is_create = True
        if 'item_id' in request.POST and request.POST['item_id'].isdigit():
            is_create = False
            id = request.POST['item_id']
            if('status' in request.POST and request.POST['status'] == 'D'):
                #update the check details with new records
                Order.objects.filter(pk=id).update(status = request.POST['status'], modified_date = datetime.now(), modified_by=request.user)
                response_data = {'is_valid':True, 'data':'Item successfully deleted'}
                return HttpResponse(json.dumps(response_data), mimetype="application/json")

        elif 'item_id' in request.POST and not request.POST['item_id'].isdigit():
            message = "Update to an invalid item"

        message = "success"
        if request.user.employee.position < permissions['Sales Representative']:
            message = "You are unauthorised to perform this action"
        elif ( is_create and (not ('accountNumber' in request.POST) or not request.POST['accountNumber'].isdigit())):
            message = "Client ID invalid, Please search and select a client"
        elif ( not ('mantruckmodel' in request.POST) or not request.POST['mantruckmodel']):
            message = "Man Truck Model required"
        elif ( not ('order_truck_subscr' in request.POST) or not request.POST['order_truck_subscr']):
            message = "Order Truck Subscription required"
        elif ( not ('gfz_number' in request.POST) or not request.POST['gfz_number']):
            message = "GFZ Number required"
        elif ( not ('truckage' in request.POST) or not request.POST['truckage']):
            message = "Please select Truck Age"
        elif ( not ('duty_type' in request.POST) or not request.POST['duty_type']):
            message = "Duty type required"
        elif ( not ('quantity' in request.POST) or not request.POST['quantity']):
            message = "Enter Quatity of items ordered"

        elif ( not ('estimated_delivery_time' in request.POST) or not request.POST['estimated_delivery_time']):
            message = "Select Estimated Delivery time"
        elif ((not 'manexprice' in request.POST) or __strType(request.POST['manexprice']) == 'str'):
            message = "Enter valid Manex Basic Veh. Price"
        elif ('additionalequipment' in request.POST and request.POST['additionalequipment'] and  __strType(request.POST['additionalequipment']) == 'str'):
            message = "Enter valid Amount for additional Equipment"
        elif ('externalequipment' in request.POST and request.POST['externalequipment'] and  __strType(request.POST['externalequipment']) == 'str'):
            message = "Enter valid Amount for external Equipment"
        elif ('othertobespecified' in request.POST and request.POST['othertobespecified'] and  __strType(request.POST['othertobespecified']) == 'str'):
            message = "Enter valid Amount for Other specified costs"
        elif ((not 'sellingprice' in request.POST) or __strType(request.POST['sellingprice']) == 'str'):
            message = "Enter a valid selling price"
        elif ( not ('payment_term' in request.POST) or not request.POST['payment_term']):
            message = "Select Payment Term to apply"
        elif ( not ('discount' in request.POST) or not request.POST['discount']):
            message = "Please supply a discount value"
        elif ( not ('specialdiscount' in request.POST) or not request.POST['specialdiscount']):
            message = "Please supply a special discount value"
        elif ( not ('country' in request.POST) or not request.POST['country']):
            message = "Please enter destination country"

        additionalequipment = request.POST['additionalequipment'] if ('additionalequipment' in request.POST and request.POST['additionalequipment']) else 0
        externalequipment = request.POST['externalequipment'] if ('externalequipment' in request.POST and request.POST['externalequipment']) else 0
        othertobespecified = request.POST['othertobespecified'] if ('othertobespecified' in request.POST and request.POST['othertobespecified']) else 0



        if ( not ('ordernumber' in request.POST) or not request.POST['ordernumber']):

            country = Country.objects.get(pk = request.POST['country'], status='A')
            NumberDate = time.strftime("%y%m%d")
            today=date.today()
            firstInitial = request.user.first_name[0]
            lastInitial = request.user.last_name[0]
            numOrder = Order.objects.filter(created_by= request.user,created_date__gte=today).count() + 2
            orderNumber = country.iso2code+NumberDate+'-'+str(numOrder)+'-'+firstInitial.upper()+lastInitial.upper()

            #Check to make sure that order number is not repeated
            orderNumberCheck = Order.objects.all().filter(order_number=orderNumber, status='A')
            if(orderNumberCheck):
                message = "Order %s number assigned to another transaction. Kindly review this accordingly" %(orderNumber)
        else:
            orderNumber = request.POST['ordernumber']



        #Check if client exists
        if(is_create):
            client = Client.objects.all().filter(client_id__iexact = request.POST['accountNumber'], status='A')
            if(not client):
                message = "Client ID does not exist. Please contact systems administrator for help"
            else:
                client = client[0]



        if(message == "success"):
            #Change dueDate to allowed date format
            day_string = ''
            if 'orderdate' in request.POST:
                d = datetime.strptime(request.POST['orderdate'],'%d-%m-%Y')
                day_string = d.strftime('%Y-%m-%d')

            if is_create:
                #Initialise and save the check details
                order = Order(    order_number = orderNumber,
                            client = client,
                            man_truck_model = request.POST['mantruckmodel'],
                            order_truck_subscr = request.POST['order_truck_subscr'],
                            gfz_number = request.POST['gfz_number'],
                            payment_term_id = request.POST['payment_term'],
                            estimated_delivery_time_id = request.POST['estimated_delivery_time'],
                            quantity = request.POST['quantity'],
                            duty_type_id = request.POST['duty_type'],
                            discount_id = request.POST['discount'],
                            special_discount_id = request.POST['specialdiscount'],
                            country_id = request.POST['country'],
                            manex_basic_vehicle_price = request.POST['manexprice'],
                            currency_id = request.POST['currency'],
                            additional_equipment = additionalequipment,
                            external_equipment = externalequipment,
                            other_to_be_equipment = othertobespecified,
                            truck_age_id = request.POST['truckage'],
                            selling_price = request.POST['sellingprice'],
                            created_by = request.user,
                            modified_by = request.user
                        )
                order.save()
            else:
                #update the order details with new records
                Order.objects.filter(pk=id).update(
                            man_truck_model = request.POST['mantruckmodel'],
                            order_truck_subscr = request.POST['order_truck_subscr'],
                            gfz_number = request.POST['gfz_number'],
                            payment_term = request.POST['payment_term'],
                            estimated_delivery_time = request.POST['estimated_delivery_time'],
                            quantity = request.POST['quantity'],
                            duty_type = request.POST['duty_type'],
                            discount = request.POST['discount'],
                            special_discount = request.POST['specialdiscount'],
                            country = request.POST['country'],
                            manex_basic_vehicle_price = request.POST['manexprice'],
                            currency = request.POST['currency'],
                            additional_equipment = additionalequipment,
                            external_equipment = externalequipment,
                            other_to_be_equipment = othertobespecified,
                            truck_age = request.POST['truckage'],
                            selling_price = request.POST['sellingprice'],
                            created_by = request.user,
                            modified_date = datetime.now(), modified_by=request.user)

            is_valid = True

            if is_create:
                message = "<b>Congratulations!</b> you have successfully created order request with Number:"+orderNumber
            else:
                message = "Order request successfully updated"


        else:
            is_valid = False
            message = "<b>Oops..</b>" + message

        response_data = {'is_valid':is_valid, 'data':message}
        return HttpResponse(json.dumps(response_data), mimetype="application/json")

    else:
        response_data = {'is_valid':False, 'data':'Please refresh your page and try again'}
        return HttpResponse(json.dumps(response_data), mimetype="application/json")

def proformaView(request):
    if request.user.is_authenticated():
        return render(request, 'proforma.html', proformaContext(request))
    else:
        return render(request, 'login.html', {})

def proformaPDF(request):
    if request.user.is_authenticated():
        return render_to_pdf2('proformaPDF.html', proformaContext(request))
    else:
        return render(request, 'login.html', {})

def proformaContext(request):
    country = Country.objects.all().filter(status='A').order_by('name')
    order = Order.objects.get(pk=request.GET['order_id'])
    calculated = {}
    calculated['SALE_PRICE'] = "%0.2f" % (round(float(order.selling_price), 2))
    calculated['SALE_PRICE_TOTAL'] = "%0.2f" % ( round(float(order.selling_price) * float(order.quantity),2))

    today = datetime.today().strftime('%m/%d/%Y')
    valid =date.today() + timedelta(days=31)
    valid = valid.strftime('%m/%d/%Y')

    calculated['DATE'] = today
    calculated['VALID'] = valid

    import os.path
    from django.conf import settings
    path = os.path.join(
            settings.MEDIA_ROOT,
            "")
    path = path.replace(settings.MEDIA_URL,"")

    context = {'profile': request.user, 'creator': order.created_by, 'order':order, 'calculated':calculated, 'path':path}

    return context


def qsfView(request):
    if request.user.is_authenticated():

        country = Country.objects.all().filter(status='A').order_by('name')
        order = Order.objects.get(pk=request.GET['order_id'])
        calculated = {}
        calculated['TOTAL_PRICE'] = round(float(order.selling_price) * float(order.quantity))

        today = datetime.today().strftime('%m/%d/%Y')
        valid =date.today() + timedelta(days=31)
        valid = valid.strftime('%m/%d/%Y')

        calculated['DATE'] = today
        calculated['VALID'] = valid

        context = {'profile': request.user, 'creator': order.created_by, 'order':order, 'calculated':calculated}
        return render(request, 'qsf.html', context)
    else:
        return render(request, 'login.html', {})

def qsfPDF(request):
    if request.user.is_authenticated():

        country = Country.objects.all().filter(status='A').order_by('name')
        order = Order.objects.get(pk=request.GET['order_id'])
        calculated = {}
        calculated['TOTAL_PRICE'] = round(float(order.selling_price) * float(order.quantity))

        today = datetime.today().strftime('%m/%d/%Y')
        valid =date.today() + timedelta(days=31)
        valid = valid.strftime('%m/%d/%Y')

        calculated['DATE'] = today
        calculated['VALID'] = valid

        context = {'profile': request.user, 'creator': order.created_by, 'order':order, 'calculated':calculated}
        return render_to_pdf2('qsfPDF.html', context)
    else:
        return render(request, 'login.html', {})

def calculationView(request):
    if request.user.is_authenticated():

        country = Country.objects.all().filter(status='A').order_by('name')
        order = Order.objects.get(pk=request.GET['order_id'])

        calculated =  {'discount_on_gfz': round(float(order.manex_basic_vehicle_price)*float(order.discount.percent)/100, 2)}
        calculated['total_vehicle_price'] =  float(order.manex_basic_vehicle_price)+float(order.additional_equipment)
        calculated['discount_on_other'] =  round(float(order.additional_equipment)*float(order.discount.percent)/100, 2)
        calculated['vehicle_net_price1'] =  calculated['total_vehicle_price']-calculated['discount_on_other']-calculated['discount_on_gfz']
        calculated['vehicle_net_price2'] = calculated['vehicle_net_price1'] - float(order.special_discount.percent)*calculated['total_vehicle_price']/100

        # sea_frieght_to_tema = CustomConfiguration.objects.all().filter(configuration='SEA_FRIEGHT_TO_TEMA').values('value')
        # fob_charges = CustomConfiguration.objects.all().filter(configuration='FOB_CHARGES').values('value')
        sea_frieght_to_tema = CustomConfiguration.objects.get(configuration='SEA_FRIEGHT_TO_TEMA')#.filter(configuration='SEA_FRIEGHT_TO_TEMA')
        fob_charges = CustomConfiguration.objects.get(configuration='FOB_CHARGES')
        interest = CustomConfiguration.objects.get(configuration='INTEREST_RATE')

        transport_charge = float(sea_frieght_to_tema.value) + float(fob_charges.value)
        calculated['transport_charge'] = transport_charge
        calculated['lc_cost'] = round(float(order.payment_term.rate)/100 * int(order.payment_term.duration)/360* (transport_charge + calculated['vehicle_net_price2'] + float(order.external_equipment)),2)
        calculated['other_to_be_specified'] = round(float(order.other_to_be_equipment),2)
        calculated['external_equipment'] = round(float(order.external_equipment),2)
        calculated['interest'] = round(float(interest.value),2)
        calculated['days'] = order.payment_term.duration
        calculated['quantity'] = order.quantity

        calculated['vehicle_net_price3'] = calculated['vehicle_net_price2'] + calculated['external_equipment'] + calculated['other_to_be_specified'] + calculated['lc_cost'] + calculated['transport_charge']

        calculated['vehicle_net_price_total'] = calculated['vehicle_net_price3'] * float(order.quantity)

        now = datetime.now()
        dep_number = int(now.year) - int(order.truck_age.year)
        depreciation = Depreciation.objects.get(number=dep_number)
        calculated['purchase_price_minus_depreciation'] = (calculated['vehicle_net_price3'] - calculated['transport_charge']) * (1-(float(depreciation.percent)/100))

        cost_of_frieght = CustomConfiguration.objects.get(configuration='COST_OF_FRIEGHT')
        calculated['cost_of_frieght'] = round(float(cost_of_frieght.value))

        insurance_cost_of_frieght_percent = CustomConfiguration.objects.get(configuration='INSURANCE_ON_FREIGHT_PERCENT')
        insurance_cost_of_frieght = CustomConfiguration.objects.get(configuration='INSURANCE_ON_FREIGHT')
        calculated['insurance_on_freight'] = float(insurance_cost_of_frieght.value)
        calculated['insurance_on_freight_percent'] = float(insurance_cost_of_frieght_percent.value)
        calculated['dutiable_value'] = float(calculated['cost_of_frieght']) + float(calculated['insurance_on_freight']) + calculated['purchase_price_minus_depreciation']

        import_duties = CustomsRate.objects.get(name='IMPORT_DUTIES')
        calculated['import_duties_percent'] = import_duties.percent
        calculated['import_duties'] = float(import_duties.percent)/100*calculated['dutiable_value']
        calculated['purchase_prices_plus_duties'] = calculated['import_duties'] + calculated['insurance_on_freight'] + calculated['cost_of_frieght'] + calculated['purchase_price_minus_depreciation']

        import_duties = CustomsRate.objects.get(name='SIL')
        calculated['SIL'] = import_duties.percent
        calculated['SIL_V'] = float(import_duties.percent)*calculated['dutiable_value']/100
        import_duties = CustomsRate.objects.get(name='IMPORT_NHIL')
        calculated['IMPORT_NHIL'] = import_duties.percent
        calculated['IMPORT_NHIL_V'] = float(import_duties.percent)*calculated['purchase_prices_plus_duties']/100
        import_duties = CustomsRate.objects.get(name='NET_WORK_CHARGE')
        calculated['NET_WORK_CHARGE'] = import_duties.percent
        calculated['NET_WORK_CHARGE_V'] = float(import_duties.percent)*calculated['purchase_price_minus_depreciation']/100
        import_duties = CustomsRate.objects.get(name='VEHICLE_EXAMINATION')
        calculated['VEHICLE_EXAMINATION'] = import_duties.percent
        calculated['VEHICLE_EXAMINATION_V'] = float(import_duties.percent)*calculated['dutiable_value']/100
        import_duties = CustomsRate.objects.get(name='EXPORT_DEVISE_LEVI')
        calculated['EXPORT_DEVISE_LEVI'] = import_duties.percent
        calculated['EXPORT_DEVISE_LEVI_V'] = float(import_duties.percent)*calculated['dutiable_value']/100
        import_duties = CustomsRate.objects.get(name='ECOWAX_LEVI')
        calculated['ECOWAX_LEVI'] = import_duties.percent
        calculated['ECOWAX_LEVI_V'] = float(import_duties.percent)*calculated['dutiable_value']/100
        import_duties = CustomsRate.objects.get(name='PROCESS_FEE')
        calculated['PROCESS_FEE'] = import_duties.percent
        calculated['PROCESS_FEE_V'] = float(import_duties.percent)*calculated['purchase_prices_plus_duties']/100
        import_duties = CustomsRate.objects.get(name='IMPORT_EXCISE')
        calculated['IMPORT_EXCISE'] = import_duties.percent
        calculated['IMPORT_EXCISE_V'] = float(import_duties.percent)*calculated['purchase_prices_plus_duties']/100
        import_duties = CustomsRate.objects.get(name='IMPORT_SPECIAL_TAX')
        calculated['IMPORT_SPECIAL_TAX'] = import_duties.percent
        calculated['IMPORT_SPECIAL_TAX_V'] = float(import_duties.percent)*calculated['purchase_prices_plus_duties']/100
        import_duties = CustomsRate.objects.get(name='VAT')
        calculated['VAT'] = import_duties.percent
        calculated['VAT_V'] = float(import_duties.percent)*calculated['purchase_prices_plus_duties']/100
        import_duties = CustomsRate.objects.get(name='IMPORT_DUTIES')
        calculated['IMPORT_DUTIES'] = import_duties.percent
        calculated['IMPORT_DUTIES_V'] = float(import_duties.percent)*calculated['dutiable_value']/100
        import_duties = CustomsRate.objects.get(name='NET_CHARGE_NHIL')
        calculated['NET_CHARGE_NHIL'] = import_duties.percent
        calculated['NET_CHARGE_NHIL_V'] = import_duties.percent * calculated['NET_WORK_CHARGE_V'] / 100
        import_duties = CustomsRate.objects.get(name='NET_CHARGE_VAT')
        calculated['NET_CHARGE_VAT'] = import_duties.percent
        calculated['NET_CHARGE_VAT_V'] = import_duties.percent * calculated['NET_WORK_CHARGE_V'] / 100

        calculated['TOTAL_DUTY_PLUS_VAT'] = calculated['IMPORT_DUTIES_V']+calculated['SIL_V']+calculated['IMPORT_NHIL_V']+calculated['NET_WORK_CHARGE_V']+calculated['VEHICLE_EXAMINATION_V']+calculated['EXPORT_DEVISE_LEVI_V']+calculated['ECOWAX_LEVI_V']\
                                            +calculated['PROCESS_FEE_V']+calculated['IMPORT_EXCISE_V']+calculated['IMPORT_SPECIAL_TAX_V']+calculated['VAT_V']+calculated['NET_CHARGE_NHIL_V']+calculated['NET_CHARGE_VAT_V']

        current_exchange_rate = CustomConfiguration.objects.get(configuration='CURRENT_EXCHANGE_RATE')
        calculated['DUTIES_IN_GHC'] = float(current_exchange_rate.value)*calculated['TOTAL_DUTY_PLUS_VAT']


        cost = CustomConfiguration.objects.get(configuration='SHIPPING_LINE_LOCAL_COST_GHC')
        calculated['SHIPPING_LINE_LOCAL_COST'] = float(cost.value)/float(current_exchange_rate.value)
        cost = CustomConfiguration.objects.get(configuration='SAFE_BOND_COST_GHC')
        calculated['SAFE_BOND_COST'] = float(cost.value)/float(current_exchange_rate.value)
        cost = CustomConfiguration.objects.get(configuration='CLEARING_AGENT_COST_GHC')
        calculated['CLEARING_AGENT_COST'] = float(cost.value)/float(current_exchange_rate.value)
        cost = CustomConfiguration.objects.get(configuration='WAREHOUSING_COSTS_GHC')
        calculated['WAREHOUSING_COSTS'] = float(cost.value)/float(current_exchange_rate.value)
        cost = CustomConfiguration.objects.get(configuration='FUEL_COST_GHC')
        calculated['FUEL_COST'] = float(cost.value)/float(current_exchange_rate.value)
        cost = CustomConfiguration.objects.get(configuration='MISCELLANEOUS_COST_GHC')
        calculated['MISCELLANEOUS_COST'] = float(cost.value)/float(current_exchange_rate.value)
        cost = CustomConfiguration.objects.get(configuration='TRAIL_NUMBER_COST_GHC')
        calculated['TRAIL_NUMBER_COST'] = float(cost.value)/float(current_exchange_rate.value)

        calculated['TOTAL_LOCAL_COST'] = calculated['SHIPPING_LINE_LOCAL_COST']+calculated['SAFE_BOND_COST']+calculated['CLEARING_AGENT_COST']+calculated['WAREHOUSING_COSTS']\
                                          +calculated['FUEL_COST']+calculated['MISCELLANEOUS_COST']+calculated['TRAIL_NUMBER_COST']

        calculated['TOTAL_DUTIIES_PLUS_LOCAL_COST'] = (float(order.duty_type.percent)*calculated['TOTAL_DUTY_PLUS_VAT']/100)+calculated['TOTAL_LOCAL_COST']
        calculated['TOTAL_DUTIIES_PLUS_LOCAL_COST_IN_GHC'] = calculated['TOTAL_DUTIIES_PLUS_LOCAL_COST']*float(current_exchange_rate.value)


        calculated2 =  {}
        calculated2['MANEXPRICE'] =  round(float(order.manex_basic_vehicle_price) + float(order.additional_equipment))
        calculated2['DISCOUNT_MAN'] =  round((float(order.manex_basic_vehicle_price) + float(order.additional_equipment))*float(order.discount.percent)/100 )
        calculated2['EXTERNAL_EQUIPMENT'] = round(float(order.external_equipment))
        calculated2['SPECIAL_DISCOUNT'] = round((float(order.manex_basic_vehicle_price) + float(order.additional_equipment))*float(order.special_discount.percent)/100 )
        calculated2['FOB_CHARGES'] = round(float(fob_charges.value))
        calculated2['SEA_FRIEGHT_TO_TEMA'] = 2898.55
        calculated2['GROSS_CFR_PRICE_1'] = calculated2['MANEXPRICE'] - calculated2['DISCOUNT_MAN'] + calculated2['EXTERNAL_EQUIPMENT'] - calculated2['SPECIAL_DISCOUNT'] + calculated2['FOB_CHARGES'] + calculated2['SEA_FRIEGHT_TO_TEMA']
        calculated2['LC_COST'] = round(calculated2['GROSS_CFR_PRICE_1'] * float(order.payment_term.rate)/100 * float(order.payment_term.duration)/360)
        calculated2['GROSS_CFR_PRICE_2'] = round(calculated2['GROSS_CFR_PRICE_1'] + calculated2['LC_COST'])
        calculated2['VAT_DUTIES_CLEARING_COSTS'] = round(calculated['TOTAL_DUTIIES_PLUS_LOCAL_COST'])
        calculated2['GROSS_CFR_PRICE_INC_DUTIES_PLUS_VAT'] = calculated2['GROSS_CFR_PRICE_2'] + calculated2['VAT_DUTIES_CLEARING_COSTS']

        bank_charge_percent = CustomConfiguration.objects.get(configuration='LOCAL_BANK_CHARGE_PERCENT')
        bank_charge_percent = CustomConfiguration.objects.get(configuration='LOCAL_BANK_CHARGE_PERCENT')

        calculated2['LOCAL_BANK_CHARGES_PERCENT'] = bank_charge_percent.value
        calculated2['LOCAL_BANK_CHARGES'] = round(float(bank_charge_percent.value)/100 * calculated2['GROSS_CFR_PRICE_2'])

        registration_cost = CustomConfiguration.objects.get(configuration='REGISTRATION_COSTS_GHC')
        calculated2['REGISTRATION_COSTS_GHC'] = registration_cost.value
        calculated2['REGISTRATION_COSTS'] = float(registration_cost.value)/float(current_exchange_rate.value)

        registration_cost = CustomConfiguration.objects.get(configuration='SERVICE_COST_WORKSHOP')
        calculated2['SERVICE_COST_WORKSHOP'] = float(registration_cost.value)
        calculated2['EXTRA_BANK_CHARGE'] = round(calculated2['GROSS_CFR_PRICE_INC_DUTIES_PLUS_VAT'] * float(order.payment_term.extra_bank_rate)/100 * float(order.payment_term.duration)/360)
        calculated2['MBG_TOTAL_COST_P_U_PLUS_VAT_PLUS_DUTIES'] = calculated2['GROSS_CFR_PRICE_INC_DUTIES_PLUS_VAT'] + calculated2['LOCAL_BANK_CHARGES'] + \
                                                                 calculated2['REGISTRATION_COSTS'] + calculated2['SERVICE_COST_WORKSHOP'] + calculated2['EXTRA_BANK_CHARGE']
        calculated2['UNIT_PRICE_EX_VAT_NHILL'] = round(calculated2['MBG_TOTAL_COST_P_U_PLUS_VAT_PLUS_DUTIES']*100/115)
        calculated2['MARGIN_VALUE'] = round(float(order.selling_price)-calculated2['MBG_TOTAL_COST_P_U_PLUS_VAT_PLUS_DUTIES'])
        calculated2['MARGIN_PERCENT'] = round(calculated2['MARGIN_VALUE']/calculated2['MBG_TOTAL_COST_P_U_PLUS_VAT_PLUS_DUTIES']*100, 2)
        calculated2['SALES_PRICE_EX_VAT_NHILL'] = calculated2['MARGIN_VALUE'] + calculated2['UNIT_PRICE_EX_VAT_NHILL']


        # vat_for_customer = CustomConfiguration.objects.get(configuration='VAT_FOR_CUSTOMER')
        calculated2['VAT_FOR_CUSTOMER'] = round(float(order.duty_type.vat_percentage) * calculated2['SALES_PRICE_EX_VAT_NHILL'])
        calculated2['VAT_FOR_CUSTOMER_PERCENT'] = order.duty_type.vat_percentage
        calculated2['SALE_PRICE_INC_VAT_NHILL'] = order.selling_price

        calculated2['VAT_FROM_MBG'] = round(calculated2['MBG_TOTAL_COST_P_U_PLUS_VAT_PLUS_DUTIES']*15/115)
        calculated2['VAT_FROM_CUSTOMER'] = round(calculated2['VAT_FOR_CUSTOMER'])
        calculated2['VAT_TO_CONTRIBUTE_OUTGOING'] = calculated2['VAT_FROM_CUSTOMER'] - calculated2['VAT_FROM_MBG']
        calculated2['UNIT_MARGIN'] = calculated2['MARGIN_VALUE']
        calculated2['TOTAL_MARGIN'] = calculated2['MARGIN_VALUE'] * float(order.quantity)









# UNIT PRICE EX VAT/NHILL
# NET-MARGIN


# GROSS CFR PRICE INC DUTIES + VAT
# LOCAL BANK CHARGES
# REGISTRATION COSTS
# SERVICE COSTS/WORKSHOP
# EXTRA CHARGES L/C BANK COSTS


# UNIT PRICE EX VAT/NHILL

# GROSS_CFR_PRICE_INC_DUTIES_PLUS_VAT



        context = {'profile': request.user, 'creator': order.created_by, 'order':order, 'calculated':calculated, 'calculated2':calculated2}
        return render(request, 'calculation.html', context)
    else:
        return render(request, 'login.html', {})

def mofView(request):
    if request.user.is_authenticated():

        country = Country.objects.all().filter(status='A').order_by('name')
        order = Order.objects.get(pk=request.GET['order_id'])

        calculated =  {'discount_on_gfz': round(float(order.manex_basic_vehicle_price)*float(order.discount.percent)/100, 2)}
        calculated['total_vehicle_price'] =  float(order.manex_basic_vehicle_price)+float(order.additional_equipment)
        calculated['discount_on_other'] =  round(float(order.additional_equipment)*float(order.discount.percent)/100, 2)
        calculated['vehicle_net_price1'] =  calculated['total_vehicle_price']-calculated['discount_on_other']-calculated['discount_on_gfz']
        calculated['vehicle_net_price2'] = calculated['vehicle_net_price1'] - float(order.special_discount.percent)*calculated['total_vehicle_price']/100

        # sea_frieght_to_tema = CustomConfiguration.objects.all().filter(configuration='SEA_FRIEGHT_TO_TEMA').values('value')
        # fob_charges = CustomConfiguration.objects.all().filter(configuration='FOB_CHARGES').values('value')
        sea_frieght_to_tema = CustomConfiguration.objects.get(configuration='SEA_FRIEGHT_TO_TEMA')#.filter(configuration='SEA_FRIEGHT_TO_TEMA')
        fob_charges = CustomConfiguration.objects.get(configuration='FOB_CHARGES')
        interest = CustomConfiguration.objects.get(configuration='INTEREST_RATE')

        transport_charge = float(sea_frieght_to_tema.value) + float(fob_charges.value)
        calculated['transport_charge'] = transport_charge
        calculated['lc_cost'] = round(float(order.payment_term.rate)/100 * int(order.payment_term.duration)/360* (transport_charge + calculated['vehicle_net_price2'] + float(order.external_equipment)),2)
        calculated['other_to_be_specified'] = round(float(order.other_to_be_equipment),2)
        calculated['external_equipment'] = round(float(order.external_equipment),2)
        calculated['interest'] = round(float(interest.value),2)
        calculated['days'] = order.payment_term.duration
        calculated['quantity'] = order.quantity

        calculated['vehicle_net_price3'] = calculated['vehicle_net_price2'] + calculated['external_equipment'] + calculated['other_to_be_specified'] + calculated['lc_cost'] + calculated['transport_charge']

        calculated['vehicle_net_price_total'] = calculated['vehicle_net_price3'] * float(order.quantity)

        context = {'profile': request.user, 'creator': order.created_by, 'order':order, 'calculated':calculated}
        return render(request, 'mof.html', context)
    else:
        return render(request, 'login.html', {})

def mofPDF(request):
    if request.user.is_authenticated():

        country = Country.objects.all().filter(status='A').order_by('name')
        order = Order.objects.get(pk=request.GET['order_id'])

        calculated =  {'discount_on_gfz': round(float(order.manex_basic_vehicle_price)*float(order.discount.percent)/100, 2)}
        calculated['total_vehicle_price'] =  float(order.manex_basic_vehicle_price)+float(order.additional_equipment)
        calculated['discount_on_other'] =  round(float(order.additional_equipment)*float(order.discount.percent)/100, 2)
        calculated['vehicle_net_price1'] =  calculated['total_vehicle_price']-calculated['discount_on_other']-calculated['discount_on_gfz']
        calculated['vehicle_net_price2'] = calculated['vehicle_net_price1'] - float(order.special_discount.percent)*calculated['total_vehicle_price']/100

        # sea_frieght_to_tema = CustomConfiguration.objects.all().filter(configuration='SEA_FRIEGHT_TO_TEMA').values('value')
        # fob_charges = CustomConfiguration.objects.all().filter(configuration='FOB_CHARGES').values('value')
        sea_frieght_to_tema = CustomConfiguration.objects.get(configuration='SEA_FRIEGHT_TO_TEMA')#.filter(configuration='SEA_FRIEGHT_TO_TEMA')
        fob_charges = CustomConfiguration.objects.get(configuration='FOB_CHARGES')
        interest = CustomConfiguration.objects.get(configuration='INTEREST_RATE')

        transport_charge = float(sea_frieght_to_tema.value) + float(fob_charges.value)
        calculated['transport_charge'] = transport_charge
        calculated['lc_cost'] = round(float(order.payment_term.rate)/100 * int(order.payment_term.duration)/360* (transport_charge + calculated['vehicle_net_price2'] + float(order.external_equipment)),2)
        calculated['other_to_be_specified'] = round(float(order.other_to_be_equipment),2)
        calculated['external_equipment'] = round(float(order.external_equipment),2)
        calculated['interest'] = round(float(interest.value),2)
        calculated['days'] = order.payment_term.duration
        calculated['quantity'] = order.quantity

        calculated['vehicle_net_price3'] = calculated['vehicle_net_price2'] + calculated['external_equipment'] + calculated['other_to_be_specified'] + calculated['lc_cost'] + calculated['transport_charge']

        calculated['vehicle_net_price_total'] = calculated['vehicle_net_price3'] * float(order.quantity)

        calculated['total_vehicle_price_list'] = round(float(order.additional_equipment)+ float(order.manex_basic_vehicle_price),2)
        calculated['special_discount_amount'] = round(calculated['total_vehicle_price_list']*float(order.special_discount.percent)/100,2)


        context = {'profile': request.user, 'creator': order.created_by, 'order':order, 'calculated':calculated}

        return render_to_pdf('mofPDF.html', context)
        # return render(request, 'mof.html', context)
    else:
        return render(request, 'login.html', {})

def __strType(var):
    try:
        if int(var) == float(var):
            return 'int'
    except:
        try:
            float(var)
            return 'float'
        except:
            return 'str'