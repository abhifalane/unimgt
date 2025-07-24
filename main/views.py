from django.shortcuts import render,HttpResponse
from django.shortcuts import render, redirect
from .models import Student, Subject
from django.core.files.storage import FileSystemStorage
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Student, Subject, StudentAssignment
from django.contrib.auth import logout
from django.contrib.auth.models import User
from .models import UserProfile
from django.db.models import Avg, Count, Q
import xlwt
from django.http import HttpResponse
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import authenticate, login, logout


def dashboard(request):
    return render(request, 'dashboard.html')
def student_register(request):
    if request.method == 'POST':
        name = request.POST['name']
        father_name = request.POST['father_name']
        roll_no = request.POST['roll_no']
        mobile = request.POST['mobile']
        college = request.POST['college']
        dob = request.POST['dob']
        photo = request.FILES['photo']
        subjects = request.POST.getlist('subjects[]')

        student = Student(name=name, father_name=father_name, roll_no=roll_no, mobile=mobile, college=college, dob=dob, photo=photo)
        student.save()

        for subject in subjects:
            Subject.objects.create(student=student, subject_name=subject)

        return render(request, 'register_success.html', {'student': student})

    return render(request, 'student_register.html')

def admin_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user and user.is_staff:
            login(request, user)
            return redirect('admin_dashboard')
        else:
            return render(request, 'admin_login.html', {'error': 'Invalid Credentials'})
    return render(request, 'admin_login.html')

@login_required
def admin_dashboard(request):
    students = Student.objects.all()
    return render(request, 'templates/admin_dashboard.html', {'students': students})

@login_required
def add_marks(request, student_id):
    student = Student.objects.get(id=student_id)
    subjects = Subject.objects.filter(student=student)

    if request.method == 'POST':
        for subject in subjects:
            marks = request.POST.get(f'marks_{subject.id}')
            subject.marks = int(marks)
            subject.save()
        return redirect('admin_dashboard')

    return render(request, 'add_marks.html', {'student': student, 'subjects': subjects})

def student_login(request):
    if request.method == 'POST':
        roll_no = request.POST['roll_no']
        dob = request.POST['dob']

        try:
            student = Student.objects.get(roll_no=roll_no, dob=dob)
            request.session['student_id'] = student.id
            return redirect('student_dashboard')
        except Student.DoesNotExist:
            return render(request, 'student_login.html', {'error': 'Invalid roll number or DOB'})

    return render(request, 'student_login.html')

def student_admit_card(request):
    student_id = request.session.get('student_id')
    if not student_id:
        return redirect('student_login')

    student = Student.objects.get(id=student_id)
    subjects = Subject.objects.filter(student=student)

    return render(request, 'admit_card.html', {
        'student': student,
        'subjects': subjects
    })
def student_logout(request):
    try:
        del request.session['student_id']
    except KeyError:
        pass
    return redirect('student_login')

def entry_login(request):
    if request.method == 'POST':
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        if user and user.userprofile.role == 'entry':
            login(request, user)
            return redirect('entry_dashboard')
        return render(request, 'entry_login.html', {'error': 'Invalid'})
    return render(request, 'entry_login.html')

@login_required
def entry_dashboard(request):
    if request.user.userprofile.role != 'entry':
        return HttpResponse("Unauthorized", status=401)

    assigned_students = StudentAssignment.objects.filter(entry_user=request.user)
    return render(request, 'entry_dashboard.html', {'assignments': assigned_students})

@login_required
def entry_add_marks(request, student_id):
    student = Student.objects.get(id=student_id)
    subjects = Subject.objects.filter(student=student)

    if request.method == 'POST':
        for subject in subjects:
            subject.marks = int(request.POST.get(f'marks_{subject.id}'))
            subject.save()
        return redirect('entry_dashboard')

    return render(request, 'entry_add_marks.html', {'student': student, 'subjects': subjects})

def allocate_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        role = request.POST['role']

        if User.objects.filter(username=username).exists():
            return render(request, 'allocate_user.html', {'error': 'Username already exists.'})

        user = User.objects.create_user(username=username, password=password)
        UserProfile.objects.create(user=user, role=role)
        return render(request, 'allocate_user.html', {'message': f"User '{username}' created and allocated as {role}."})

    return render(request, 'allocate_user.html')

@login_required
def user_list(request):
    users = User.objects.all().order_by('username')
    return render(request, 'user_list.html', {'users': users})

def edit_user(request, user_id):
    user = User.objects.get(id=user_id)
    profile = UserProfile.objects.get(user=user)

    if request.method == 'POST':
        user.username = request.POST['username']
        password = request.POST.get('password')
        if password:
            user.set_password(password)
        user.save()

        profile.role = request.POST['role']
        profile.save()

        return redirect('user_list')

    return render(request, 'edit_user.html', {'user': user, 'profile': profile})

def delete_user(request, user_id):
    user = User.objects.get(id=user_id)
    user.delete()
    return redirect('user_list')

def student_result(request):
    student_id = request.session.get('student_id')
    if not student_id:
        return redirect('student_login')

    student = Student.objects.get(id=student_id)
    subjects = Subject.objects.filter(student=student)

    # Result logic
    total = 0
    passed = True
    max_marks = 100  # assume 100 per subject
    for s in subjects:
        if s.marks is None or s.marks < 33:
            passed = False
        total += s.marks or 0

    percentage = round(total / (len(subjects) * max_marks) * 100, 2)
    result_status = "PASS" if passed else "FAIL"

    return render(request, 'student_result.html', {
        'student': student,
        'subjects': subjects,
        'total': total,
        'percentage': percentage,
        'result_status': result_status
    })
def student_dashboard(request):
    student_id = request.session.get('student_id')
    if not student_id:
        return redirect('student_login')

    student = Student.objects.get(id=student_id)
    subjects = Subject.objects.filter(student=student)
    return render(request, 'student_dashboard.html', {
        'student': student,
        'subjects': subjects
    })

@login_required
def report_statistics(request):
    classes = Class.objects.all()
    selected_class_id = request.GET.get('class_id')

    context = {'classes': classes}

    if selected_class_id:
        selected_class = Class.objects.get(id=selected_class_id)
        students = Student.objects.filter(student_class=selected_class)

        student_data = []
        pass_count = 0
        total_students = students.count()
        topper = None
        highest_percentage = 0
        total_percentage = 0

        for student in students:
            results = Result.objects.filter(student=student)
            total = sum(r.marks_obtained for r in results)
            max_marks = sum(r.max_marks for r in results)

            if max_marks == 0:
                continue

            percentage = (total / max_marks) * 100
            status = "PASS" if all(r.marks_obtained >= r.max_marks * 0.33 for r in results) else "FAIL"

            if status == "PASS":
                pass_count += 1

            total_percentage += percentage

            if percentage > highest_percentage:
                highest_percentage = percentage
                topper = student

            student_data.append({
                'student': student,
                'total': total,
                'max_marks': max_marks,
                'percentage': round(percentage, 2),
                'status': status,
            })

        avg_percentage = round(total_percentage / total_students, 2) if total_students > 0 else 0
        fail_count = total_students - pass_count

        context.update({
            'selected_class': selected_class,
            'student_data': student_data,
            'total_students': total_students,
            'pass_count': pass_count,
            'fail_count': fail_count,
            'avg_percentage': avg_percentage,
            'topper': topper,
            'highest_percentage': round(highest_percentage, 2),
        })

    return render(request, 'report_statistics.html', context)

def export_result_excel(request, student_id):
    student = Student.objects.get(id=student_id)
    results = Result.objects.filter(student=student)

    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = f'attachment; filename="{student.roll_number}_Result.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Result')

    headers = ['Subject', 'Type', 'Marks Obtained', 'Max Marks', 'Remarks']
    for col_num in range(len(headers)):
        ws.write(0, col_num, headers[col_num])

    for row_num, result in enumerate(results, start=1):
        ws.write(row_num, 0, result.subject_assignment.subject.name)
        ws.write(row_num, 1, result.subject_assignment.subject_type)
        ws.write(row_num, 2, result.marks_obtained)
        ws.write(row_num, 3, result.max_marks)
        ws.write(row_num, 4, result.remarks)

    wb.save(response)
    return response

@login_required
def change_password(request):
    if request.method == 'POST':
        old_pass = request.POST['old_password']
        new_pass = request.POST['new_password']
        user = request.user

        if user.check_password(old_pass):
            user.set_password(new_pass)
            user.save()
            update_session_auth_hash(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'change_password.html', {'error': 'Old password incorrect'})

    return render(request, 'change_password.html')

def admin_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user and user.is_staff:
            login(request, user)
            return redirect('admin_dashboard')
        else:
            return render(request, 'admin_login.html', {'error': 'Invalid Credentials'})
    return render(request, 'admin_login.html')

@login_required
def admin_dashboard(request):
    students = Student.objects.all()
    return render(request, 'admin_dashboard.html', {'students': students})

@login_required
def add_marks(request, student_id):
    student = Student.objects.get(id=student_id)
    subjects = Subject.objects.filter(student=student)

    if request.method == 'POST':
        for subject in subjects:
            marks = request.POST.get(f'marks_{subject.id}')
            subject.marks = int(marks)
            subject.save()
        return redirect('admin_dashboard')

    return render(request, 'add_marks.html', {'student': student, 'subjects': subjects})