from django.shortcuts import render

# Create your views here.
def trading_account(request):
    return render(request,'management/tradingaccount.html')