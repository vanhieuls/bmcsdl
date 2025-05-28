from django.core.exceptions import ValidationError
from django.shortcuts import render
from django.contrib import messages
from django.contrib import auth
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.http import urlencode


from .models import User, Candidate, Vote
from .forms import LoginForm, RegisterForm, ChangePasswordForm


def check_authentication(f):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return f(request, *args, **kwargs)
        else:
            redirect_url = reverse('vote:login')
            parameters = urlencode({
                'next': request.path
            })
            return redirect(f"{redirect_url}?{parameters}")

    return wrapper


@check_authentication
def index(request):
    # print("User is authenticated:", request.user.district)
    candidates = Candidate.objects.filter(district=request.user.district)

    return render(request, 'vote/index.html', context={
        'candidates': candidates,
    })


def login(request):
    if request.user.is_authenticated:
        return redirect('vote:index')

    next_url = request.GET.get('next', reverse('vote:index'))

    if request.method == 'POST':
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            id = login_form.cleaned_data['id']
            password = login_form.cleaned_data['password']

            user = auth.authenticate(username=id, password=password)

            if user is not None:
                auth.login(request, user)
                if user.is_staff:
                    return redirect('admin:index')
                if next_url:
                    return redirect(next_url)
                return redirect('vote:index')  # fallback cuối

            # nếu sai tài khoản
            return render(request, 'vote/login.html', {
                'login_form': login_form,
                'next': next_url,
                'error': 'Sai tài khoản hoặc mật khẩu.'
            })

        # ❗ THÊM return này nếu form không hợp lệ
        return render(request, 'vote/login.html', {
            'login_form': login_form,
            'next': next_url,
            'error': 'Form không hợp lệ. Vui lòng kiểm tra lại.'
        })

    # GET request
    return render(request, 'vote/login.html', context={
        'next': next_url,
        'login_form': LoginForm(),
    })


def logout(request):
    auth.logout(request)
    return redirect('vote:login')


def register(request):
    if request.user.is_authenticated:
        return redirect('vote:index')

    next_url = request.GET.get('next', reverse('vote:index'))

    if request.method == 'POST':
        register_form = RegisterForm(request.POST)

        if register_form.is_valid():
            id = register_form.cleaned_data['id']
            name = register_form.cleaned_data['name']
            password = register_form.cleaned_data['password']
            password_confirm = register_form.cleaned_data['password_confirm']
            birthdate = register_form.cleaned_data['birthdate']
            address = register_form.cleaned_data['address']
            district = register_form.cleaned_data['district']
            email = register_form.cleaned_data['email']
            if password != password_confirm:
                return redirect('vote:register')
            if User.objects.filter(id=id).exists():
                return redirect('vote:register')
            user = User.objects.create_user(
                id=id,
                password=password,
                name=name,
                birthdate=birthdate,
                address=address,
                district=district,
                email=email
            )
            auth.login(request, user)
            return redirect(next_url)

    return render(request, 'vote/register.html', context={
        'next': next_url,
        'register_form': RegisterForm(),
    })


def candidate_detail(request, candidate_id):
    if not request.user.is_authenticated:
        return redirect('vote:index')

    c = get_object_or_404(Candidate, id=candidate_id)

    return render(request, 'vote/candidate_detail.html', context={
        'candidate': c,
    })


def vote(request, candidate_id):
    if not request.user.is_authenticated:
        return redirect('vote:index')

    c = get_object_or_404(Candidate, id=candidate_id)

    if request.method == 'POST':
        v = Vote.objects.create(
            candidate=c,
            user=request.user.id,
        )
        v.cast_vote()
        messages.success(request, 'Bỏ phiếu thành công!')
        return redirect('vote:index')

    return redirect('vote:index')


def change_password(request):
    if not request.user.is_authenticated:
        return redirect('vote:index')

    if request.method == 'POST':
        change_password_form = ChangePasswordForm(request.POST)

        if change_password_form.is_valid():
            old_password = change_password_form.cleaned_data['old_password']
            new_password = change_password_form.cleaned_data['new_password']
            confirm_new_password = change_password_form.cleaned_data['confirm_new_password']

            if not request.user.check_password(old_password):
                messages.error(request, 'Mật khẩu cũ không đúng.')
                return redirect('vote:change_password')

            if new_password != confirm_new_password:
                messages.error(request, 'Mật khẩu mới không khớp.')
                return redirect('vote:change_password')

            request.user.set_password(new_password)
            request.user.save()
            messages.success(request, 'Đổi mật khẩu thành công!')
            return redirect('vote:index')
    else:
        change_password_form = ChangePasswordForm()
    return render(request, 'vote/change_password.html', context={
        'change_password_form': change_password_form,
    })
