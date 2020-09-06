from django.shortcuts import render , redirect
from .models import Product, Contact, Orders, OrderUpdate
from math import ceil
import json
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from .PayTm import Checksum
# Create your views here.
from django.http import HttpResponse
MERCHANT_KEY = 'Your merchant key'
from django.conf import settings
from django.conf.urls.static import static
from .forms import Signup1 , Verify , Loginx
from .models import AddUser 
from django.contrib import messages
from django.contrib.auth.models import User
from random import randint
from django.core.mail import send_mail,EmailMessage
def mainhome(request):
	return render(request,'mainhome.html')
def index(request):
    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prod = Product.objects.filter(category=cat)
        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        allProds.append([prod, range(1, nSlides), nSlides])
    params = {'allProds':allProds}
    return render(request, 'index.html', params)

def searchMatch(query, item):
    '''return true only if query matches the item'''
    if query in item.desc.lower() or query in item.product_name.lower() or query in item.category.lower():
        return True
    else:
        return False

def search(request):
    query = request.GET.get('search')
    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prodtemp = Product.objects.filter(category=cat)
        prod = [item for item in prodtemp if searchMatch(query, item)]

        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        if len(prod) != 0:
            allProds.append([prod, range(1, nSlides), nSlides])
    params = {'allProds': allProds, "msg": ""}
    if len(allProds) == 0 or len(query)<4:
        params = {'msg': "Please make sure to enter relevant search query"}
    return render(request, 'search.html', params)


def about(request):
    return render(request, 'about.html')


def contact(request):
    thank = False
    if request.method=="POST":
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        desc = request.POST.get('desc', '')
        contact = Contact(name=name, email=email, phone=phone, desc=desc)
        contact.save()
        thank = True
    return render(request, 'contact.html', {'thank': thank})


def tracker(request):
    if request.method=="POST":
        orderId = request.POST.get('orderId', '')
        email = request.POST.get('email', '')
        try:
            order = Orders.objects.filter(order_id=orderId, email=email)
            if len(order)>0:
                update = OrderUpdate.objects.filter(order_id=orderId)
                updates = []
                for item in update:
                    updates.append({'text': item.update_desc, 'time': item.timestamp})
                    response = json.dumps({"status":"success", "updates": updates, "itemsJson": order[0].items_json}, default=str)
                return HttpResponse(response)
            else:
                return HttpResponse('{"status":"noitem"}')
        except Exception as e:
            return HttpResponse('{"status":"error"}')

    return render(request, 'tracker.html')


def productView(request, myid):

    # Fetch the product using the id
    product = Product.objects.filter(id=myid)
    return render(request, 'prodView.html', {'product':product[0]})


def checkout(request):
    if request.method=="POST":
        items_json = request.POST.get('itemsJson', '')
        name = request.POST.get('name', '')
        amount = request.POST.get('amount', '')
        email = request.POST.get('email', '')
        address = request.POST.get('address1', '') + " " + request.POST.get('address2', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        zip_code = request.POST.get('zip_code', '')
        phone = request.POST.get('phone', '')
        order = Orders(items_json=items_json, name=name, email=email, address=address, city=city,
                       state=state, zip_code=zip_code, phone=phone, amount=amount)
        order.save()
        update = OrderUpdate(order_id=order.order_id, update_desc="The order has been placed")
        update.save()
        thank = True
        id = order.order_id
        # return render(request, 'food order/checkout.html', {'thank':thank, 'id': id})
        # Request paytm to transfer the amount to your account after payment by user
        param_dict = {

                 'MID': 'Your merchant id ',
                'ORDER_ID': str(order.order_id),
                'TXN_AMOUNT': str(amount),
                'CUST_ID': email,
                'INDUSTRY_TYPE_ID': 'Retail',
                'WEBSITE': 'WEBSTAGING',
                'CHANNEL_ID': 'WEB',
                'CALLBACK_URL':'http://127.0.0.1:8000/handlerequest/',

        }
        param_dict['CHECKSUMHASH'] = Checksum.generate_checksum(param_dict, MERCHANT_KEY)
        return render(request, 'paytm.html', {'param_dict': param_dict})

    return render(request, 'checkout.html')


@csrf_exempt
def handlerequest(request):
    # paytm will send you post request here
    form = request.POST
    response_dict = {}
    for i in form.keys():
        response_dict[i] = form[i]
        if i == 'CHECKSUMHASH':
            checksum = form[i]

    verify = Checksum.verify_checksum(response_dict, MERCHANT_KEY, checksum)
    if verify:
        if response_dict['RESPCODE'] == '01':
            print('order successful')
        else:
            print('order was not successful because' + response_dict['RESPMSG'])
    return render(request, 'paymentstatus.html', {'response': response_dict})
class Signup ( View ):
    def get(self , request):
        messages.error(request,"Method is not correct")
        return render ( request , "mainhome.html")

    def post(self , request):
        form = Signup1 ( request.POST )
        if request.method == "POST":
            if form.is_valid ( ):
                password = form.cleaned_data['Password']
                cpass = form.cleaned_data['Cpassword']
                email = form.cleaned_data['Email']
                try:
                    AddUser.objects.get ( Email = email )

                except AddUser.DoesNotExist as e:
                    if password == cpass:
                        otp = []
                        for var in range ( 4 ):
                            otp.append ( str ( randint ( 0 , 9 ) ) )
                        otp = ''.join ( otp )
                        message = "Hey Check this out \nYour OTP for verification is %s " % (otp)
                        subject = " ActivePortal-Email Verification"
                        from_email = "activeportal.in.net1998@gmail.com"
                        to_email = email
                        try:
                            send_mail ( subject , message , from_email , (email ,) ,
                                        auth_password = settings.EMAIL_HOST_PASSWORD )
                            request.session['OTP'] = int ( otp )
                            request.session['email'] = email
                            request.session['pass'] = password
                            FirstName = form.cleaned_data['FirstName']
                            request.session['FirstName'] = FirstName
                            #Password = form.cleaned_data['Password']
                            error = "Check your email for otp"
                            return render ( request , "enter.html" , {'error': error} )
                        except Exception as e:
                            error = "Try Again {}".format ( e )
                            return render ( request , "mainhome.html" , {'error': error} )
                    else:
                        error = "Password does not matched try again!!"
                        return render ( request , "mainhome.html" , {'error': error} )
                else:
                    messages.error(request,"Sorry!User Already Exist")
                    return render ( request , "mainhome.html")
            else:
                messages.error(request,"something went wrong ")
                return render ( request , "mainhome.html")
        else:
            messages.error(request,"something went wrong")
            return render ( request , "mainhome.html")


class verify ( View ):
    def get(self , request):

        del request.session['OTP']
        del request.session['email']
        del request.session['pass']
        del request.session['FirstName']
        messages.error(request,"Not valid method try again!!")
        return render ( request , "mainhome.html")

    def post(self , request):

        form = Verify ( request.POST )

        if form.is_valid ( ):

            print("value")
            otp = request.session['OTP']
            otp1 = form.cleaned_data['otp1']

            print ( otp )
            print ( otp1 )

            if otp == otp1:
                del request.session['OTP']


                data = {

                    'FirstName': request.session['FirstName'] ,
                    'Email': request.session['email'] ,
                    'Password': request.session['pass']
                }



                new_user = AddUser.objects.create ( **data )
                new_user.save ( )
                del request.session['email']
                del request.session['pass']
                del request.session['FirstName']
                messages.success( request , " You Are Successfully Signup" )
                messages.info(request,"Please Login in Our Portal And Access Our ActivePortal")
                return render ( request , "form.html" )
            else:
                error = "Invalid OTP"
                del request.session['OTP']
                del request.session['email']
                del request.session['pass']
                del request.session['FirstName']
                messages.error(request, error)
                return render ( request , "mainhome.html")

        else:
            error = "Form invalid"
            del request.session['OTP']
            del request.session['email']
            del request.session['pass']
            del request.session['FirstName']
            return render ( request , 'mainhome.html' , {'error': error} )


class Login1 ( View ):
    def get(self , request):
        messages.error(request,"Something went wrong")
        return render ( request , "mainhome.html")

    def post(self , request):
        form = Loginx ( request.POST )
        print ( form )
        if request.method == "POST":
            if form.is_valid ( ):
                data = {
                    'email': form.cleaned_data['Email'] ,
                    'password': form.cleaned_data['Password'] ,
                }
                try:
                    email = form.cleaned_data['Email']
                    password = form.cleaned_data['Password']
                    u = AddUser.objects.get ( Email = email )
                    p = u.Password
                    
                    if p == password:
                        request.session['email'] = email
                        request.session['islogin'] = True
                        messages.success ( request , "successfully logged in wel-come" )
                        return render ( request , "index.html" )
                    else:
                        messages.error ( request , "Wrong Password" )
                        return render ( request , 'mainhome.html')
                except AddUser.DoesNotExist as e:
                    messages.error ( request , "User does not exist please signup to login" )
                    return render ( request , "mainhome.html" )
            else:
                messages.error(request,"facing problem")
                return render ( request , "mainhome.html" )
def handleLogout(request):
    
    messages.success ( request , "successfully Logged Out" )
    return render ( request,"mainhome.html" )
