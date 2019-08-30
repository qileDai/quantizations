from django.shortcuts import render

# Create your views here.
def trading_account(request):
    return render(request,'management/tradingaccount.html')

def girding(request):
    return render(request,'management/gridding.html')

def index(request):
    return render(request,'management/index.html')