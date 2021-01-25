from math import ceil
from django.shortcuts import render
from  django.http import HttpResponse
from .models import Product,Contact,Orders,OrderUpdate
import json
from django.views.decorators.csrf import csrf_exempt
from .PayTm import Checksum
MERCHANT_KEY="your merchant key"


# Create your views here.
def index(request):
    # products=Product.objects.all()
    # print(products)
    # n=len(products)

   #ceil was not imported from math.ceil()

   #starting range from 1 cz there i otherwise start from 0 which is anyways active so the place we are applying i should start from 1

    allProds=[]
    catProd=Product.objects.values('category','prod_id')
    cats={item['category'] for item in catProd} #doubt in this
    for cat in cats:
        prod = Product.objects.filter(category=cat)
        n = len(prod)
        nslides = n // 4 + ceil((n / 4) - (n // 4))

        allProds.append([prod,range(1,nslides),nslides])


    # params={"no_of_slides":nslides,'range':range(1,nslides),'product':products}
    # below all prods was for demo,we need to send category wise
    # allProds=[[products,range(1,nslides),nslides],
    #           [products,range(1,nslides),nslides]]
    params={'allProds':allProds}
    return render(request,'shop/index.html',params)

def searchMatch(query, item):
    '''return true only if query matches the item'''
    if query in item.prod_desc.lower() or query in item.prod_name.lower() or query in item.category.lower():
        return True
    else:
        return False

def search(request):
    query = request.GET.get('search')
    allProds = []
    catprods = Product.objects.values('category', 'prod_id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prodtemp = Product.objects.filter(category=cat)
        prod = [item for item in prodtemp if searchMatch(query, item)]

        n = len(prod)
        nslides = n // 4 + ceil((n / 4) - (n // 4))
        if len(prod) != 0:
            allProds.append([prod, range(1, nslides), nslides])
    params = {'allProds': allProds, "msg": ""}

    # 0 means nothing written just clicked on search and <3 means atleast the word should have 3 letters like men
    # if written me or anything such won't return result
    
    if len(allProds) == 0 or len(query)<3:
        params = {'msg': "Please make sure to enter relevant search query"}
    return render(request, 'shop/search.html', params)



def about(request):
    return render(request,'shop/about.html')

def contact(request):
    if request.method=='POST':
        namee=request.POST.get('name','')
        phonee = request.POST.get('phone', '')
        emaill = request.POST.get('email', '')
        descc = request.POST.get('desc', '')
        # So 1st word is of db n 2nd is the ones in which you are accepting
        contact=Contact(name=namee,email=emaill,phone=phonee,desc=descc)
        contact.save()
        thank=True
        #for getting alert

        return render(request,'shop/contact.html', {'thank': thank})
    return render(request, 'shop/contact.html')


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
                    response = json.dumps({"status": "success", "updates": updates, "itemsJson": order[0].items_json},
                                          default=str)

                return HttpResponse(response)
            else:
                return HttpResponse('{"status":"noitem"}')
        except Exception as e:
            return HttpResponse('{"status":"error"}')

    return render(request, 'shop/tracker.html')




def products(request,myid):
    #Fetch product using id
    myprod = Product.objects.filter(prod_id=myid)
    return render(request,'shop/productview.html',{'product':myprod[0]})

def checkout(request):
    if request.method == 'POST':
        itemsJson=request.POST.get('itemsJson','')
        namee = request.POST.get('name', '')
        phonee = request.POST.get('phone', '')
        emaill = request.POST.get('email', '')
        amount = request.POST.get('amount', '')
        address = request.POST.get('address1', '') + "" + request.POST.get('address2', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        zip_code = request.POST.get('zip_code', '')
        order = Orders(items_json=itemsJson,name=namee, email=emaill,amount=amount, phone=phonee, address=address, city=city, state=state,
                       zip_code=zip_code)
        order.save()
        update=OrderUpdate(order_id=order.order_id,update_desc="Order has been placed")
        update.save()
        thank = True
        id = order.order_id
        # sending id so that user can recieve that in alert msg
        #comment the following for paytm
        return render(request, 'shop/checkout.html', {'thank': thank, 'id': id})

        # So 1st word is of db n 2nd is the ones in which you are accepting
       #rememebr it should match with the 'name' u r giving in html file(like zip_code,itemsJson check)

        #uncomment the following for paytm
        # param_dict = {
        #
        #     'MID': 'Your-Merchant-Id-Here',
        #     'ORDER_ID': str(order.order_id),
        #     'TXN_AMOUNT': str(amount),
        #     'CUST_ID': emaill,
        #     'INDUSTRY_TYPE_ID': 'Retail',
        #     'WEBSITE': 'WEBSTAGING',
        #     'CHANNEL_ID': 'WEB',
        #     'CALLBACK_URL': 'http://127.0.0.1:8000/shop/handlerequest/',
        #
        # }
        # param_dict['CHECKSUMHASH'] = Checksum.generate_checksum(param_dict, MERCHANT_KEY)
        # return render(request, 'shop/paytm.html', {'param_dict': param_dict})


    return render(request, 'shop/checkout.html')

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
    return render(request, 'shop/paymentstatus.html', {'response': response_dict})