from django.shortcuts import redirect,render
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.models import User
from .forms import RegisterForm
# Create your views here.


def loginView(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == "POST":
        data = request.POST
        user = authenticate(request, username=data['Username'], password=data['Password'])
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            return render(request, 'templates/login.html', {'message': "Username and/or password incorrect"})
    else:
        return render(request, 'templates/login.html')


def logoutView(request):
    logout(request)
    return redirect('index')


def registerView(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            data = request.POST
            new_user = User.objects.create_user(data['username'], data['email'], data['password1'])
            new_user.first_name = data['first_name']
            new_user.last_name = data['last_name']
            new_user.save()
            login(request, new_user)
            return redirect('index')
        else:
            return render(request, 'templates/register.html', {'form': form})
    else:
        return render(request, 'templates/register.html', {'form': RegisterForm()})