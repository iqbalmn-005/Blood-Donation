# pyrefly: ignore [missing-import]
from django.db.models import Q
# pyrefly: ignore [missing-import]
from django.shortcuts import render, redirect
from .models import Donor, AdminCredential

# Create your views here.

def index(request):
    donors = Donor.objects.all()
    blood_group = request.GET.get('blood_group')
    district = request.GET.get('district')
    
    if blood_group and blood_group != "SELECT BLOOD GROUP":
        donors = donors.filter(blood_group=blood_group)
    if district and district != "Select District":
        donors = donors.filter(district=district)

    donor_id = request.session.get('donor_id')
    current_donor = None
    if donor_id:
        current_donor = Donor.objects.filter(id=donor_id).first()

    return render(request, "index.html", {
        'donors': donors,
        'selected_blood_group': blood_group,
        'selected_district': district,
        'current_donor': current_donor
    })

def signup(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        blood_group = request.POST.get('blood_group', '')
        district = request.POST.get('district', '')
        phone_number = request.POST.get('phone_number', '').strip()

        if Donor.objects.filter(phone_number=phone_number).exists():
            return render(request, "signup.html", {
                'error': 'This phone number is already registered. Please login or use a different phone number.'
            })

        Donor.objects.create(
            first_name=first_name,
            email=email,
            password=password,
            blood_group=blood_group,
            district=district,
            phone_number=phone_number
        )
        return redirect('login')
    
    return render(request, "signup.html")

def login(request):
    if request.session.get('donor_id'):
        return redirect('user')

    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        password = request.POST.get('password')
        try:
            donor = Donor.objects.get(phone_number=phone_number, password=password)
            request.session['donor_id'] = donor.id
            return redirect('user')
        except Donor.DoesNotExist:
            return render(request, "login.html", {'error': 'Invalid Phone Number or Password'})

    return render(request, "login.html")

def user(request):
    donor_id = request.session.get('donor_id')
    if not donor_id:
        return redirect('login')
    try:
        donor = Donor.objects.get(id=donor_id)
    except Donor.DoesNotExist:
        return redirect('login')

    if request.method == 'POST':
        date_str = request.POST.get('last_donation_date')
        if date_str:
            donor.last_donation_date = date_str
            donor.save()
        return redirect('user')

    return render(request, "user.html", {'donor': donor})

def logout(request):
    request.session.flush()
    return redirect('index')

# Admin Views

def get_admin_cred():
    cred = AdminCredential.objects.first()
    if not cred:
        cred = AdminCredential.objects.create(username='admin', password='admin')
    return cred

def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        cred = get_admin_cred()

        if username == cred.username and password == cred.password:
            request.session['is_admin'] = True
            return redirect('admin_dashboard')
        else:
            return render(request, "admin_login.html", {'error': 'Invalid Admin Username or Password'})
    return render(request, "admin_login.html")

def admin_change_password(request):
    if not request.session.get('is_admin'):
        return redirect('admin_login')

    cred = get_admin_cred()

    if request.method == 'POST':
        username = request.POST.get('username')
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if current_password != cred.password:
            return render(request, "admin_change_password.html", {'error': 'Current password is incorrect.'})

        if new_password != confirm_password:
            return render(request, "admin_change_password.html", {'error': 'New password and confirm password do not match.'})

        if not new_password:
            return render(request, "admin_change_password.html", {'error': 'New password cannot be empty.'})

        if username:
            cred.username = username
        cred.password = new_password
        cred.save()

        return render(request, "admin_change_password.html", {'success': 'Admin password updated successfully! You can now log in with your new password.'})

    return render(request, "admin_change_password.html")

def admin_dashboard(request):
    if not request.session.get('is_admin'):
        return redirect('admin_login')

    donors = Donor.objects.all().order_by('-id')
    search_query = request.GET.get('search', '').strip()

    if search_query:
        donors = donors.filter(
            Q(first_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone_number__icontains=search_query) |
            Q(district__icontains=search_query) |
            Q(blood_group__icontains=search_query)
        )

    all_donors = list(donors)
    total_count = len(all_donors)
    available_count = sum(1 for d in all_donors if d.is_available)
    cooldown_count = total_count - available_count

    return render(request, "admin_dashboard.html", {
        'donors': all_donors,
        'total_count': total_count,
        'available_count': available_count,
        'cooldown_count': cooldown_count,
        'search_query': search_query
    })

def delete_donor(request, donor_id):
    if not request.session.get('is_admin'):
        return redirect('admin_login')
    if request.method == 'POST':
        Donor.objects.filter(id=donor_id).delete()
    return redirect('admin_dashboard')

def admin_logout(request):
    request.session.pop('is_admin', None)
    return redirect('admin_login')