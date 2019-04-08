from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import *
from django.views.decorators.csrf import csrf_protect
from datetime import date, datetime, timedelta
from django.contrib import messages
from django.utils.timezone import make_aware
from django.core.mail import send_mail
from django.conf import settings
import xlrd, xlwt
from braces import views
from django.contrib.auth.models import User
from django.db.models import Q
from .forms import LeaveForm
from .forms import TranscriptForm


def is_hod(user):
    return False if not Hod.objects.filter(user=user) else True

def is_faculty(user):
     return False if not Faculty.objects.filter(user=user) else True
def index(request):
    return render(request, 'home1.html',{})


def login_success(request):
    return HttpResponse("Success!")

@login_required
def student(request):
    student = Student.objects.get(user=request.user)
    context ={
        'student' : student,
    }
    return render(request, "student.html",)


@csrf_protect
def loginform(request):

    if request.user.is_authenticated:
        if request.user.is_staff:
                return redirect('/admin')
        if Hod.objects.filter(user=request.user):
            return redirect('/hod')
        if Faculty.objects.filter(user=request.user):
            return redirect('/faculty')
        return redirect('/student')

    if request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if request.user.is_staff:
                return redirect('/admin')
            if Hod.objects.filter(user=request.user):
                return redirect('/hod')
            if Faculty.objects.filter(user=request.user):
                return redirect('/faculty')
            return redirect('student')
        else:
            messages.add_message(request, messages.INFO,  "Incorrect username or password", extra_tags='red')
            print('Not able to authenticate')

    return render(request, "sign-in.html", {})


@login_required
def logoutform(request):
    logout(request)
    return render(request, "logout.html", {})

@login_required
@user_passes_test(is_hod)
def hod(request):
    hod = Hod.objects.get(user=request.user)
    leaves = Leave.objects.filter(department=Hod.department).order_by('approved', '-id')
    context = {
        'option':1,
        'warden': hod,
        'leaves': leaves,
    }
    postContext = {}
    if request.GET:
        name = request.GET.get('name')
        date = request.GET.get('date')
        leavesearch=[]
        for leave in leaves:
            if name.lower() in leave.student.name.lower():
                dt=str(leave.dateTimeStart.year)+'-'+str(leave.dateTimeStart.month).zfill(2)+'-'+str(leave.dateTimeStart.day).zfill(2)
                if date == "" or date in dt:
                    leavesearch.append(leave)
        postContext = {
            'leaves':leavesearch
        }
    return render(request, "warden.html", dict(context, **postContext))
    return render(request,"warden.html",{})

@login_required
@user_passes_test(is_faculty)
def faculty(request):
    faculty = Faculty.objects.filter(user=request.user)
    return render(request, "hostelsuperintendent.html", context)

def leave(request):
    student = Student.objects.get(user=request.user)
    form = LeaveForm()
    context = {
        'option' : 0,
        'student': student,
        'form': form
    }

    leaveContext = {
        'leaves': Leave.objects.filter(student=student),
    }

    if request.POST:
        form = LeaveForm(request.POST)
        if form.is_valid():
            leaveform = form.save(commit=False)
            dateStart = datetime.strptime(request.POST.get('dateStart'), '%d %B, %Y').date()
            timeStart = datetime.strptime(request.POST.get('timeStart'), '%H:%M').time()
            dateTimeStart = datetime.combine(dateStart, timeStart)
            dateEnd = datetime.strptime(request.POST.get('dateEnd'), '%d %B, %Y').date()
            timeEnd = datetime.strptime(request.POST.get('timeEnd'), '%H:%M').time()
            dateTimeEnd = datetime.combine(dateEnd, timeEnd)
            leaveform.corrPhone = request.POST.get('phone_number')
            leaveform.dateTimeStart = make_aware(dateTimeStart)
            leaveform.dateTimeEnd = make_aware(dateTimeEnd)
            leaveform.student = student
            print(request.POST.get('consent'))
            leaveform.save()
            if config.EMAIL_PROD:
                email_to=[Warden.objects.get(hostel=HostelPS.objects.get(student=student).hostel).email]
            else:
                email_to=["swdbitstest@gmail.com"]                                                                     # For testing 
            mailObj=Leave.objects.latest('id')
            mail_subject="New Leave ID: "+ str(mailObj.id)
            mail_message="Leave Application applied by "+ mailObj.student.name +" with leave id: " + str(mailObj.id) + ".\n"
            mail_message=mail_message + "Parent name: " + mailObj.student.parentName + "\nParent Email: "+ mailObj.student.parentEmail + "\nParent Phone: " + mailObj.student.parentPhone
            mail_message=mail_message + "\nConsent type: " + mailObj.consent
            send_mail(mail_subject,mail_message,settings.EMAIL_HOST_USER,email_to,fail_silently=False)

            context = {
                'option': 1,
                'dateStart': request.POST.get('dateStart'),
                'dateEnd': request.POST.get('dateEnd'),
                'timeStart': request.POST.get('timeStart'),
                'timeEnd': request.POST.get('timeEnd'),
            }
        else:
            context = {
                'option': 2,
                'form': form
            }
            print(form.errors)
    return render(request, "leave.html", dict(context, **leaveContext))

def transcript(request):
    #student = Student.objects.get(user=request.user)
    form = TranscriptForm()
    context = {
        'option' : 0,
        #'student': student,
        'form': form
    }

    transcriptContext = {
        #'transcripts': Transcript.objects.filter(student=student),
    }

    if request.POST:
        form = TranscriptForm(request.POST)
        if form.is_valid():
            transcriptform = form.save(commit=False)
            transcriptform.corrId = request.POST.get('idNo')
            transcriptform.corrname = request.POST.get('name')
            transcriptform.corrhostel = request.POST.get('hostel')
            transcriptform.corrroomNo = request.POST.get('roomNo')
            transcriptform.ps2Station = request.POST.get('ps2Station')
            transcriptform.email = request.POST.get('email')
            transcriptform.phone_number = request.POST.get('phone_number')
            transcriptform.origTranscript = request.POST.get('origTranscript')
            transcriptform.dupTranscript = request.POST.get('dupTranscript')
            transcriptform.forwardingLetters = request.POST.get('forwardingLetters')
            transcriptform.post_doc = request.POST.get('post_doc')
            transcriptform.refno = request.POST.get('refno')
            #transcriptform.dateTimeStart = make_aware(dateTimeStart)
            #leaveform.dateTimeEnd = make_aware(dateTimeEnd)
            
            #transcriptform.amtcal=200*origTranscript+(100*dupTranscript)
            
            #transcriptform.student = student
            print(request.POST.get('refno'))
    
            transcriptform.save()

            context = {
                'option': 1,
                'idNo': request.POST.get('idNo'),
                'dupTranscript': request.POST.get('dupTranscript'),
            }
        else:
            context = {
                'option': 2,
                'form': form
            }
            print(form.errors)
    return render(request, "transcript.html", dict(context, **transcriptContext))


