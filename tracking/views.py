from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.models import User, auth
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import logout, authenticate
from django.contrib import messages
from django.http import HttpResponse
from .models import Document, Types, ActionTaken, Routed,Outgoing,Carboncopy
from .myforms import AddDocumentForm, AddOnlineDocumentForm, OutgoingForm, ReuploadOnlineDocumentForm, DenyOnlineDocumentForm, \
    AcceptDocumentForm, EditDocumentForm, RouteDocumentForm, TypeForm, TypeActionForm, SendApprovedDocumentForm, \
    Edit_TypeActionForm, Edit_TypeForm
from django.template.loader import get_template
from xhtml2pdf import pisa
import datetime
from django.utils import timezone
from django.core.files.storage import FileSystemStorage
import qrcode
from PIL import Image
import os


# Create your views here.
def home(request):
    return render(request, 'home.html')


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)
        if user:
            auth.login(request, user)
            messages.success(request, ' ')
            return redirect('dashboard')
        else:
            messages.info(request, ' ')
            return render(request, 'login.html')
    else:
        return render(request, 'login.html')


def logout_view(request):  # logout view
    if request.method == 'GET':
        logout(request)
        return redirect('home')


def add_document(request):  # add docs via walkin

    form = AddDocumentForm()
    if request.method == 'POST':
        form = AddDocumentForm(request.POST, request.FILES)
        u = request.POST.get('route')
        x = User.objects.get(id=u)
        code = request.POST.get('code')
        fs = FileSystemStorage(location='static/qrcode_images/')
        if form.is_valid():
            form.save()
            print(code)
            form1 = Routed.objects.create(routed_to=x, sender=request.user.username, doc_code=code)
            form1.save()
            #img = qrcode.make(code)
            #img.save(fs.location + '/' + str(code) + ".jpg")

            logo = Image.open('static\images\MGBlogo1.jpg')
            basewidth = 70
            wpercent = (basewidth / float(logo.size[0]))
            hsize = int((float(logo.size[1]) * float(wpercent)))
            logo = logo.resize((basewidth, hsize), Image.ANTIALIAS)
            img_qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H)
            img_qr.add_data(code)
            # img = qrcode.make(code)# orig code
            img_qr.make()
            img_f = img_qr.make_image(fill_color='#0b4e39', back_color='white').convert('RGB')
            pos = ((img_f.size[0] - logo.size[0]) // 2, (img_f.size[1] - logo.size[1]) // 2)
            img_f.paste(logo, pos)
            img_f.save(fs.location + '/' + str(code) + ".jpg")  # orig code
            return redirect('dashboard')
    context = {'form': form}
    return render(request, 'add_document.html', context)


def accept_document(request, pk):  # accept the document at online received docs
    docid = Document.objects.get(id=pk)
    form = AcceptDocumentForm(instance=docid)
    if request.method == 'POST':
        docid.online = True
        docid.process = True
        u = request.POST.get('route')
        x = User.objects.get(id=u)
        code = request.POST.get('code')
        form = AcceptDocumentForm(request.POST, instance=docid)
        fs = FileSystemStorage(location='static/qrcode_images/')
        if form.is_valid():
            form.save()
            form1 = Routed.objects.create(routed_to=x, sender=request.user.username, doc_code=code)
            form1.save()
            #img = qrcode.make(code)
            #img.save(fs.location + '/' + str(code) + ".jpg")

            logo = Image.open('static\images\MGBlogo1.jpg')
            basewidth = 70
            wpercent = (basewidth / float(logo.size[0]))
            hsize = int((float(logo.size[1]) * float(wpercent)))
            logo = logo.resize((basewidth, hsize), Image.ANTIALIAS)
            img_qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H)
            img_qr.add_data(code)
            # img = qrcode.make(code)# orig code
            img_qr.make()
            img_f = img_qr.make_image(fill_color='#0b4e39', back_color='white').convert('RGB')
            pos = ((img_f.size[0] - logo.size[0]) // 2, (img_f.size[1] - logo.size[1]) // 2)
            img_f.paste(logo, pos)
            img_f.save(fs.location + '/' + str(code) + ".jpg")  # orig code
            return redirect('dashboard')
    context = {'form': form}
    return render(request, 'accept_document.html', context)


def add_online_document(request):  # adding docs via online
    form = AddOnlineDocumentForm()
    if request.method == 'POST':
        form = AddOnlineDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('display_code')
    context = {'form': form}
    return render(request, 'add_online_document.html', context)


def view_document(request):  # view all docs at dashboar or accepted docs
    current_user_id = request.user.id
    current_user = request.user.is_superuser
    current_user_division = User.objects.get(id=current_user_id)

    if current_user:  # superuser
        mineres = Document.objects.filter(complete=True, category__isnull=False, route_id=current_user_id, for_release=0).order_by(
            '-id')
        d = datetime.date.today()
        days_togo = datetime.date.today() + datetime.timedelta(days=1)
        togo = Document.objects.filter(deadline=days_togo)
        allcnt = Document.objects.filter(acted_release=0,for_release=0,complete=True, category__isnull=False).order_by('-id')
        urg = Document.objects.filter(urgent=1)
        due = Document.objects.filter(deadline__lte=d,for_release=0)
        rel = Document.objects.filter(for_release=1,acted_release=0)
        acted_rel = Document.objects.filter(for_release=1,acted_release=1)
        online_count = Document.objects.filter(category__isnull=True, online=True)
        div_res = Document.objects.filter(complete=True, category__isnull=False, acted_release=0, for_release=0,
                                          division=current_user_division.first_name).order_by('-id')
        multir = Document.objects.filter(complete=True, category__isnull=False, multiple_route=True).order_by('-id')


        if 'mine' in request.GET:  # determined what button to click
            #template_path = 'print_document.html'
            #query = request.GET.get('q', '')

            results = Document.objects.filter(complete=True, category__isnull=False, route_id = current_user_id, for_release=0).order_by('-id')

            recount = results.count
            page = request.GET.get('page', 1)
            paginator = Paginator(results, 500)
            try:
                results = paginator.page(page)
            except PageNotAnInteger:
                results = paginator.page(1)
            except EmptyPage:
                results = paginator.page(paginator.num_pages)
            context = {'result': results, 'count': recount, 'dd': d, 'urg': urg.count, 'allcnt': allcnt.count,
                       'current_user_id': current_user_id, 'current_user': current_user,
                       'online_count': online_count.count, 'togo': togo.count, 'days_togo': days_togo,
                       'due': due.count, 'rel': rel.count,'mineres':mineres.count,'acted_rel':acted_rel.count}
            return render(request, 'dashboard.html', context)


        if 'print' in request.GET:  # determined what button to click
            template_path = 'print_document.html'
            query = request.GET.get('q', '')
            if query == 'online':
                result = Document.objects.filter(online=1)
            elif query == 'mydocs':
                result = Document.objects.filter(route_id=current_user_id)
            elif query == 'urgent':
                result = Document.objects.filter(urgent=True).order_by('-id')
            elif query == 'due':
                result = Document.objects.filter(deadline__lte=d).order_by('-id')
            elif query == 'for release':
                result = Document.objects.filter(for_release=1).order_by('-id')
            else:
                result = Document.objects.filter(
                    code__iexact=query) | Document.objects.filter(category__icontains=query) | Document.objects.filter(
                    subject__icontains=query) | Document.objects.filter(
                    sender__icontains=query) | Document.objects.filter(
                    date_received__icontains=query) | Document.objects.filter(
                    description__icontains=query)

            context = {'result': result, 'count': result.count}
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'filename="inventory-report.pdf"'
            template = get_template(template_path)
            html = template.render(context)
            pisa_status = pisa.CreatePDF(html, dest=response)
            if pisa_status.err:
                return HttpResponse('Error')
            return response

        if request.method == 'GET':
            query = request.GET.get('q', '')
            squery = request.GET.get('sq', '')
            if query == '':
                results = Document.objects.filter(complete=True, category__isnull=False, for_release=0).order_by('-id')
            elif query == 'urgent':
                results = Document.objects.filter(urgent=True).order_by('-id')
            elif query == 'mydocs':
                results = Document.objects.filter(route_id=current_user_id)
            elif query == 'due':
                results = Document.objects.filter(deadline__lte=d)
            elif query == 'for release':
                results = Document.objects.filter(for_release=1)
            else:
                if squery == 'Sender':
                    results = Document.objects.filter(sender__icontains=query).order_by('-id')
                elif squery == 'Description':
                    results = Document.objects.filter(description__icontains=query).order_by('-id')
                elif squery == 'Document Code':
                    results = Document.objects.filter(code__iexact=query).order_by('-id')
                elif squery == 'Subject':
                    results = Document.objects.filter(subject__icontains=query).order_by('-id')
                else:
                    results = Document.objects.all()

            recount = results.count
            page = request.GET.get('page', 1)
            paginator = Paginator(results, 100)
            try:
                results = paginator.page(page)
            except PageNotAnInteger:
                results = paginator.page(1)
            except EmptyPage:
                results = paginator.page(paginator.num_pages)
            context = {'result': results, 'count': recount, 'dd': d, 'urg': urg.count, 'allcnt': allcnt.count,
                       'due': due.count, 'rel': rel.count, 'current_user_id': current_user_id,'multir':multir.count,
                       'current_user': current_user, 'online_count': online_count.count, 'togo': togo.count,
                       'days_togo': days_togo,'mineres': mineres.count,'acted_rel':acted_rel.count,'div_res':div_res.count}
            return render(request, 'dashboard.html', context)
    # User
    else:
        #mineres = Document.objects.filter(complete=True, category__isnull=False, route_id=current_user_id).order_by('-id')
        d = datetime.date.today()
        days_togo = datetime.date.today() + datetime.timedelta(days=1)
        togo = Document.objects.filter(deadline=days_togo, route_id=current_user_id)
        allcnt = Document.objects.filter(acted_release=0,for_release=0,complete=True, category__isnull=False, route_id=current_user_id).order_by('-id')
        urg = Document.objects.filter(urgent=1, route_id=current_user_id)
        due = Document.objects.filter(deadline__lte=d,for_release=0, route_id=current_user_id)
        dueall = Document.objects.filter(deadline__lte=d, for_release=0)
        rel = Document.objects.filter(for_release=1,acted_release=0)
        online_count = Document.objects.filter(category__isnull=True, online=True)
        multir = Document.objects.filter(complete=True, category__isnull=False, multiple_route=True).order_by('-id')
        acted_rel = Document.objects.filter(for_release=1, acted_release=1, )
        div_res = Document.objects.filter(complete=True, category__isnull=False, acted_release=0, for_release=0,
                                          division=current_user_division.first_name).order_by('-id')

        if 'print' in request.GET:  # determined what button to click
            template_path = 'print_document.html'
            query = request.GET.get('q', '')
            if query == 'online':
                result = Document.objects.filter(online=1)
            elif query == 'mydocs':
                result = Document.objects.filter(route_id=current_user_id)
            elif query == 'urgent':
                result = Document.objects.filter(urgent=True).order_by('-id')
            elif query == 'due':
                result = Document.objects.filter(deadline__lte=d).order_by('-id')
            elif query == 'for release':
                result = Document.objects.filter(for_release=1).order_by('-id')
            else:
                result = Document.objects.filter(
                    code__iexact=query) | Document.objects.filter(category__icontains=query) | Document.objects.filter(
                    subject__icontains=query) | Document.objects.filter(
                    sender__icontains=query) | Document.objects.filter(
                    type_id__type_name__icontains=query) | Document.objects.filter(
                    action_taken_id__action_taken__icontains=query) | Document.objects.filter(
                    date_received__icontains=query) | Document.objects.filter(
                    description__icontains=query)

            context = {'result': result, 'count': result.count}
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'filename="inventory-report.pdf"'
            template = get_template(template_path)
            html = template.render(context)
            pisa_status = pisa.CreatePDF(html, dest=response)
            if pisa_status.err:
                return HttpResponse('Error')
            return response


        if request.method == 'GET':
            query = request.GET.get('q', '')
            squery = request.GET.get('sq', '')
            if query == '':
                if request.user.id == 3 or request.user.id == 9:
                    results = Document.objects.filter(for_release=0,complete=True, category__isnull=False,route_id=current_user_id).order_by('id')
                else:
                    results = Document.objects.filter(for_release=0,complete=True, category__isnull=False,route_id=current_user_id,confidential=False).order_by('id')
            elif query == 'urgent':
                results = Document.objects.filter(urgent=True).order_by('id')
            elif query == 'due':
                results = Document.objects.filter(deadline__lte=d)
            #elif query == 'mydocs':
               # results = Document.objects.filter(route_id=current_user_id)
            elif query == 'for release':
                results = Document.objects.filter(for_release=0,route_id=current_user_id)
            else:
                if squery == 'Sender':
                    results = Document.objects.filter(sender__icontains=query, division__icontains=request.user.first_name).order_by('id')
                elif squery == 'Description':
                    results = Document.objects.filter(description__icontains=query, division__icontains=request.user.first_name).order_by('id')
                elif squery == 'Document Code':
                    results = Document.objects.filter(code__iexact=query, division__icontains=request.user.first_name).order_by('id')
                elif squery == 'Subject':
                    results = Document.objects.filter(subject__icontains=query, division__icontains=request.user.first_name).order_by('id')
                else:
                    results = Document.objects.all()


            recount = results.count
            page = request.GET.get('page', 1)
            paginator = Paginator(results, 100)
            try:
                results = paginator.page(page)
            except PageNotAnInteger:
                results = paginator.page(1)
            except EmptyPage:
                results = paginator.page(paginator.num_pages)
            context = {'result': results, 'count': recount, 'dd': d, 'urg': urg.count, 'allcnt': allcnt.count,
                       'current_user_id': current_user_id, 'current_user': current_user,'userN':'RD_Carido',
                       'online_count': online_count.count, 'togo': togo.count, 'days_togo': days_togo,'dueall':dueall.count,
                       'due': due.count, 'rel': rel.count, 'multir':multir.count,'acted_rel':acted_rel.count,'div_res':div_res.count}
            return render(request, 'dashboard.html', context)


def received_online(request):  # viewing all doc applied online
    result = Document.objects.filter(category__isnull=True)
    context = {'result': result}
    return render(request, 'received_online.html', context)


def display_code(request):  # display code after saving online application
    x = Document.objects.last
    context = {'code': x}
    return render(request, 'display_code.html', context)


def view_online_search(request):  # search docs at home page
    if request.method == 'GET':
        query = request.GET.get('q', '')
        if Document.objects.filter(code=query).exists():
            results = Document.objects.filter(code=query)
            context = {'result': results}
            return render(request, 'home.html', context)
        else:
            messages.info(request, 'No record found!')
            return redirect('home')


def reupload_online_document(request, pk):  # reupload the pdf
    docid = Document.objects.get(id=pk)
    form = ReuploadOnlineDocumentForm(instance=docid)
    if request.method == 'POST':
        docid.online = True
        docid.remark = ''
        form = ReuploadOnlineDocumentForm(request.POST, request.FILES, instance=docid)
        if form.is_valid():
            form.save()
            return redirect('home')
    context = {'form': form}
    return render(request, 'reupload_online_document.html', context)


def deny_online_document(request, pk):  # deny the document at online received docs

    docid = Document.objects.get(id=pk)
    form = DenyOnlineDocumentForm(instance=docid)
    if request.method == 'POST':
        form = DenyOnlineDocumentForm(request.POST, instance=docid)
        docid.online = False
        if form.is_valid():
            form.save()
            return redirect('received_online')
    context = {'form': form}
    return render(request, 'deny_online_document.html', context)


def edit_document(request, pk):  # edit the document
    docid = Document.objects.get(id=pk)
    form = EditDocumentForm(instance=docid)
    if request.method == 'POST':
        form = EditDocumentForm(request.POST, request.FILES, instance=docid)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    context = {'form': form}
    return render(request, 'edit_document.html', context)


def route_document(request, pk):  # edit the document
    docid = Document.objects.get(id=pk)
    form = RouteDocumentForm(instance=docid)
    if request.method == 'POST':
        form = RouteDocumentForm(request.POST, instance=docid)
        if form.is_valid():
            form.save()
            action_taken = request.POST['action_taken']
            route = request.POST['route']
            cfurnish = request.POST.getlist('cfurnish')  # it will give list that will use to iterate (will loop save the checked checkbox)
            code = request.POST['code']
            comment = request.POST['comment']
            fs = FileSystemStorage(location='media/attached/')
            request_file = request.FILES['filename'] if 'filename' in request.FILES else request.FILES

            xx = User.objects.get(id=route) # get the id of selected route/personnel
            Document.objects.filter(pk=pk).update(division=xx.first_name) # save/update the first_name to the division filed

            if request_file:
                file = fs.save(request_file.name, request_file)
                fileurl = fs.url('/attached/' + file)
                form_r = Routed.objects.create(doc_code=code, comment=comment, action_id=action_taken,
                                               routed_to_id=route, sender=request.user.username, attach_file=fileurl)
                form_r.save()
                for cc in cfurnish:  # will loop save the checked checkbox
                    form_c = Carboncopy.objects.create(doc_code=code, routed_to_id=cc)
                    form_c.save()

                return redirect('dashboard')
            else:
                form = Routed.objects.create(doc_code=code, comment=comment, action_id=action_taken, routed_to_id=route,
                                             sender=request.user.username, attach_file='')
                form.save()
                for cc in cfurnish:  # will loop save the checked checkbox
                    form_c = Carboncopy.objects.create(doc_code=code, routed_to_id=cc)
                    form_c.save()
        return redirect('dashboard')

    result = Routed.objects.filter(doc_code=docid.code)
    emp = User.objects.filter(is_active = True).order_by('username')
    context = {'form': form, 'result': result, 'sender': docid.sender, 'des': docid.description,'emp':emp,
               'date_received': docid.date_received, 'deadline': docid.deadline, 'subject': docid.subject}
    #context = {'form': form}
    return render(request, 'route_document.html', context)


def document_history(request, pk):  # view pdf history of docs
    template_path = 'document_history.html'
    docid = Document.objects.get(code=pk)
    result = Routed.objects.filter(doc_code=docid.code)
    context = {'result': result, 'code': docid.code, 'sender': docid.sender, 'des': docid.description,'subject':docid.subject,
               'date_received': docid.date_received, 'deadline': docid.deadline, 'pdf': 'MGBlogo.png'}
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="inventory-report.pdf"'
    template = get_template(template_path)
    html = template.render(context)
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Error')
    return response


def comment_document(request, pk):  # view pdf history of docs
    docid = Document.objects.get(code=pk)
    result = Routed.objects.filter(doc_code=docid.code)
    context = {'result': result, 'code': docid.code, 'sender': docid.sender, 'des': docid.description,
               'date_received': docid.date_received, 'deadline': docid.deadline, 'subject': docid.subject,'pdf_file':docid.pdf_file}
    return render(request, 'comment_document.html', context)

def route_history(request):  # view pdf history of docs
    current_user_name = request.user.username
    #docid = Document.objects.get(code=pk)
    result = Routed.objects.filter(sender=current_user_name)
    context = {'result': result}
    return render(request, 'route_history.html', context)


def type_of_document(request):  # edit the document
    i_type = Types.objects.all().order_by('-id')
    form = TypeForm()
    if request.method == 'POST':
        form = TypeForm(request.POST)
        type_name = request.POST['type_name']
        if form.is_valid():
            if Types.objects.filter(type_name=type_name).exists():
                messages.info(request, 'Type Name nasa database na.')
                return redirect('type_of_document')
            else:
                form.save()
                messages.info(request, 'Data saved.')
                return redirect('type_of_document')

    page = request.GET.get('page', 1)
    paginator = Paginator(i_type, 100)
    try:
        i_type = paginator.page(page)
    except PageNotAnInteger:
        i_type = paginator.page(1)
    except EmptyPage:
        i_type = paginator.page(paginator.num_pages)
    context = {'form': form, 'i_type': i_type}
    return render(request, 'type_of_document.html', context)


def type_of_action(request):  # edit the document
    actions = ActionTaken.objects.all().order_by('-id')
    form = TypeActionForm()
    if request.method == 'POST':
        form = TypeActionForm(request.POST)
        action_taken = request.POST['action_taken']
        if form.is_valid():
            if ActionTaken.objects.filter(action_taken=action_taken).exists():
                messages.info(request, 'Action Name nasa database na.')
                return redirect('type_of_action')
            else:
                form.save()
                messages.info(request, 'Data saved.')
                return redirect('type_of_action')
    page = request.GET.get('page', 1)
    paginator = Paginator(actions, 100)
    try:
        actions = paginator.page(page)
    except PageNotAnInteger:
        actions = paginator.page(1)
    except EmptyPage:
        actions = paginator.page(paginator.num_pages)
    context = {'form': form, 'actions': actions}
    return render(request, 'type_of_action.html', context)


def send_approved_document(request, pk):  # accept the document at online received docs
    docid = Document.objects.get(id=pk)
    form = SendApprovedDocumentForm(instance=docid)
    if request.method == 'POST':
        docid.date_sent = datetime.datetime.today()
        form = SendApprovedDocumentForm(request.POST, request.FILES, instance=docid)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    context = {'form': form}
    return render(request, 'send_approved_document.html', context)


def display_qrcode(request, code):
    context = {'codes': code}
    return render(request, 'display_qrcode.html', context)


def for_release(request):
    current_user_id = request.user.id
    if 'print' in request.GET:  # determined what button to click
        template_path = 'print_document.html'
        query = request.GET.get('q', '')

        result = Document.objects.filter(
            code__iexact=query) | Document.objects.filter(category__icontains=query) | Document.objects.filter(
            subject__icontains=query) | Document.objects.filter(
            sender__icontains=query) | Document.objects.filter(
            type_id__type_name__icontains=query) | Document.objects.filter(
            action_taken_id__action_taken__icontains=query) | Document.objects.filter(
            date_received__icontains=query)

        context = {'result': result, 'count': result.count}
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'filename="inventory-report.pdf"'
        template = get_template(template_path)
        html = template.render(context)
        pisa_status = pisa.CreatePDF(html, dest=response)
        if pisa_status.err:
            return HttpResponse('Error')
        return response

    if request.method == 'GET':
        query = request.GET.get('q', '')
        if query == '':
            results = Document.objects.filter(complete=True, category__isnull=False, for_release=True).order_by('-id')

        recount = results.count
        page = request.GET.get('page', 1)
        paginator = Paginator(results, 100)
        try:
            results = paginator.page(page)
        except PageNotAnInteger:
            results = paginator.page(1)
        except EmptyPage:
            results = paginator.page(paginator.num_pages)
        context = {'result': results, 'count': recount, 'current_user_id': current_user_id,
                   'release_count': results.count}
        return render(request, 'for_release.html', context)


def edit_type_of_action(request, pk):  # saving new employee
    action_id = ActionTaken.objects.get(id=pk)
    form = Edit_TypeActionForm(instance=action_id)
    if request.method == 'POST':
        form = Edit_TypeActionForm(request.POST, instance=action_id)
        if form.is_valid():
            form.save()
            return redirect('type_of_action')
    context = {'form': form}
    return render(request, 'type_of_action.html', context)


def edit_type_of_document(request, pk):  # saving new employee
    type_id = Types.objects.get(id=pk)
    form = Edit_TypeForm(instance=type_id)
    if request.method == 'POST':
        form = Edit_TypeForm(request.POST, instance=type_id)
        if form.is_valid():
            form.save()
            return redirect('type_of_document')
    context = {'form': form}
    return render(request, 'type_of_document.html', context)

def report(request):  # help

    if request.method == "POST":
        template_path = 'print_report.html'

        fromdate = request.POST.get('fromdate')
        todate = request.POST.get('todate')
        div_name = request.POST.get('division')
        result = Document.objects.raw('select id,code,category,subject,description,sender,date_received,division from tracking_document where division="'+div_name+'" and date_received between "'+fromdate+'" and "'+todate+'"')

        context = {'result': result}
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'filename="inventory-report.pdf"'
        template = get_template(template_path)
        html = template.render(context)
        pisa_status = pisa.CreatePDF(html, dest=response)
        if pisa_status.err:
            return HttpResponse('Error')
        return response
    else:
        return render(request, 'report.html')


def route_history_code(request,pk):  # click route hisroty code and view docs
     result = Document.objects.filter(code__iexact=pk)
     context ={'result':result}
     return render(request, 'route_history_code.html', context)

def acted_menu(request):
    current_user_id = request.user.id
    current_user = request.user.is_superuser
    # mineres = Document.objects.filter(complete=True, category__isnull=False, route_id=current_user_id).order_by('-id')
    d = datetime.date.today()
    days_togo = datetime.date.today() + datetime.timedelta(days=1)
    togo = Document.objects.filter(deadline=days_togo, route_id=current_user_id)
    allcnt = Document.objects.filter(acted_release=0,for_release=0,complete=True, category__isnull=False,route_id=current_user_id).order_by('-id')
    allcnt_super = Document.objects.filter(acted_release=0, for_release=0, complete=True, category__isnull=False).order_by('-id')
    urg = Document.objects.filter(urgent=1, route_id=current_user_id)
    due = Document.objects.filter(deadline__lte=d, route_id=current_user_id)
    rel = Document.objects.filter(for_release=1, acted_release=0)
    online_count = Document.objects.filter(category__isnull=True, online=True)
    multir = Document.objects.filter(complete=True, category__isnull=False, multiple_route=True).order_by('-id')
    acted_rel = Document.objects.filter(for_release=1, acted_release=1, )

    if 'print' in request.GET:  # determined what button to click
        template_path = 'print_document.html'
        query = request.GET.get('q', '')

        if query == '':
            result = Document.objects.filter(online=1,for_release=1).order_by('-id')
        elif query == '':
            result = Document.objects.filter(route_id=current_user_id,for_release=1).order_by('-id')
        elif query == 'urgent':
            result = Document.objects.filter(urgent=True,for_release=1).order_by('-id')
        elif query == 'due':
            result = Document.objects.filter(deadline__lte=d,for_release=1).order_by('-id')
        elif query == 'for release':
            result = Document.objects.filter(route_id=current_user_id,for_release=1).order_by('-id')
        else:
            result = Document.objects.filter(
                code__iexact=query) | Document.objects.filter(category__icontains=query) | Document.objects.filter(
                subject__icontains=query) | Document.objects.filter(
                sender__icontains=query) | Document.objects.filter(
                date_received__icontains=query) | Document.objects.filter(
                description__icontains=query)

        context = {'result': result, 'count': result.count}
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'filename="inventory-report.pdf"'
        template = get_template(template_path)
        html = template.render(context)
        pisa_status = pisa.CreatePDF(html, dest=response)
        if pisa_status.err:
            return HttpResponse('Error')
        return response

    if request.method == 'GET':
        query = request.GET.get('q', '')
        if query == '':
            results = Document.objects.filter(for_release=1, acted_release=0).order_by('-id')
        else:
            results = Document.objects.filter(
            code__iexact=query) | Document.objects.filter(category__icontains=query) | Document.objects.filter(
            subject__icontains=query) | Document.objects.filter(
            sender__icontains=query) | Document.objects.filter(
            type_id__type_name__icontains=query) | Document.objects.filter(
            action_taken_id__action_taken__icontains=query) | Document.objects.filter(
            date_received__icontains=query) | Document.objects.filter(
            description__icontains=query)

        recount = results.count
        page = request.GET.get('page', 1)
        paginator = Paginator(results, 500)
        try:
            results = paginator.page(page)
        except PageNotAnInteger:
            results = paginator.page(1)
        except EmptyPage:
            results = paginator.page(paginator.num_pages)
        context = {'result': results, 'count': recount, 'dd': d, 'urg': urg.count, 'allcnt': allcnt.count,
                   'current_user_id': current_user_id, 'current_user': current_user,
                   'online_count': online_count.count, 'togo': togo.count, 'days_togo': days_togo,
                   'due': due.count, 'rel': rel.count, 'multir': multir.count, 'acted_rel': acted_rel.count,'allcnt_super':allcnt_super.count}
        return render(request, 'acted_dashboard.html', context)

def copy_furnish(request):
    current_user_id = request.user.id
    current_user = request.user.is_superuser
    # mineres = Document.objects.filter(complete=True, category__isnull=False, route_id=current_user_id).order_by('-id')
    d = datetime.date.today()
    days_togo = datetime.date.today() + datetime.timedelta(days=1)
    togo = Document.objects.filter(deadline=days_togo, route_id=current_user_id)
    allcnt = Document.objects.filter(acted_release=0,for_release=0,complete=True, category__isnull=False,route_id=current_user_id).order_by('-id')
    allcnt_super = Document.objects.filter(acted_release=0, for_release=0, complete=True, category__isnull=False,).order_by('-id')
    urg = Document.objects.filter(urgent=1, route_id=current_user_id)
    due = Document.objects.filter(deadline__lte=d, route_id=current_user_id)
    rel = Document.objects.filter(for_release=1, acted_release=0)
    online_count = Document.objects.filter(category__isnull=True, online=True)
    #multir = Document.objects.filter(complete=True, category__isnull=False, multiple_route=True).order_by('-id')
    acted_rel = Document.objects.filter(for_release=1, acted_release=1, )

    if 'print' in request.GET:  # determined what button to click
        template_path = 'print_document.html'
        query = request.GET.get('q', '')

        if query == 'online':
            result = Document.objects.filter(online=1).order_by('-id')
        elif query == '':
            result = Document.objects.filter(route_id=current_user_id,for_release=1).order_by('-id')
        elif query == 'urgent':
            result = Document.objects.filter(urgent=True,for_release=1).order_by('-id')
        elif query == 'due':
            result = Document.objects.filter(deadline__lte=d,for_release=1).order_by('-id')
        elif query == 'for release':
            result = Document.objects.filter(for_release=1,route_id=current_user_id).order_by('-id')
        else:
            result = Document.objects.filter(
                code__iexact=query) | Document.objects.filter(category__icontains=query) | Document.objects.filter(
                subject__icontains=query) | Document.objects.filter(
                sender__icontains=query) | Document.objects.filter(
                type_id__type_name__icontains=query) | Document.objects.filter(
                action_taken_id__action_taken__icontains=query) | Document.objects.filter(
                date_received__icontains=query) | Document.objects.filter(
                description__icontains=query)

        context = {'result': result, 'count': result.count}
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'filename="inventory-report.pdf"'
        template = get_template(template_path)
        html = template.render(context)
        pisa_status = pisa.CreatePDF(html, dest=response)
        if pisa_status.err:
            return HttpResponse('Error')
        return response

    if request.method == 'GET':
        query = request.GET.get('q', '')
        if query == '':
            results = Document.objects.filter(complete=True, category__isnull=False, multiple_route=True).order_by('-id')
        else:
            results = Document.objects.filter(
            code__iexact=query) | Document.objects.filter(category__icontains=query) | Document.objects.filter(
            subject__icontains=query) | Document.objects.filter(
            sender__icontains=query) | Document.objects.filter(
            type_id__type_name__icontains=query) | Document.objects.filter(
            action_taken_id__action_taken__icontains=query) | Document.objects.filter(
            date_received__icontains=query) | Document.objects.filter(
            description__icontains=query)

        recount = results.count
        page = request.GET.get('page', 1)
        paginator = Paginator(results, 100)
        try:
            results = paginator.page(page)
        except PageNotAnInteger:
            results = paginator.page(1)
        except EmptyPage:
            results = paginator.page(paginator.num_pages)

            # for ccopy in Carboncopy.objects.raw('select id,doc_code from tracking_carboncopy where routed_to_id=%s',[current_user_id] or [current_user]):  # display its corresponding docs nga nka route sa iya
            #    display_doc = [str(ccopy.doc_code)]
            #    print(display_doc)

        copyko = Carboncopy.objects.filter(routed_to_id=current_user_id) | Carboncopy.objects.filter(
                routed_to_id=current_user)  # another way of displaying list of copy furnish

        context = {'result': results, 'count': recount, 'dd': d, 'urg': urg.count, 'allcnt': allcnt.count,'mycopy':copyko,
                   'current_user_id': current_user_id, 'current_user': current_user,'allcnt_super': allcnt_super.count,
                   'online_count': online_count.count, 'togo': togo.count, 'days_togo': days_togo,
                   'due': due.count, 'rel': rel.count, 'multir': copyko.count, 'acted_rel': acted_rel.count}
        return render(request, 'copy_furnish.html', context)

def my_docu_dashboard(request):  # view all docs at dashboar or accepted docs
    current_user_id = request.user.id
    current_user = request.user.is_superuser

    if current_user:  # superuser
        mineres = Document.objects.filter(complete=True, category__isnull=False, route_id=current_user_id, for_release=0).order_by(
            '-id')
        d = datetime.date.today()
        days_togo = datetime.date.today() + datetime.timedelta(days=1)
        togo = Document.objects.filter(deadline=days_togo)
        allcnt = Document.objects.filter(acted_release=0,for_release=0,complete=True, category__isnull=False).order_by('-id')
        urg = Document.objects.filter(urgent=1)
        due = Document.objects.filter(deadline__lte=d)
        rel = Document.objects.filter(for_release=1,acted_release=0)
        acted_rel = Document.objects.filter(for_release=1,acted_release=1)
        online_count = Document.objects.filter(category__isnull=True, online=True)


        if 'print' in request.GET:  # determined what button to click
            template_path = 'print_document.html'
            query = request.GET.get('q', '')
            if query == 'online':
                result = Document.objects.filter(online=1,route_id=current_user_id).order_by('-id')
            elif query == '':
                result = Document.objects.filter(route_id=current_user_id).order_by('-id')
            elif query == 'urgent':
                result = Document.objects.filter(urgent=True,route_id=current_user_id).order_by('-id')
            elif query == 'due':
                result = Document.objects.filter(deadline__lte=d,route_id=current_user_id).order_by('-id')
            elif query == 'for release':
                result = Document.objects.filter(for_release=1,route_id=current_user_id).order_by('-id')
            else:
                result = Document.objects.filter(
                    code__iexact=query) | Document.objects.filter(category__icontains=query) | Document.objects.filter(
                    subject__icontains=query) | Document.objects.filter(
                    sender__icontains=query) | Document.objects.filter(
                    type_id__type_name__icontains=query) | Document.objects.filter(
                    action_taken_id__action_taken__icontains=query) | Document.objects.filter(
                    date_received__icontains=query) | Document.objects.filter(
                    description__icontains=query)

            context = {'result': result, 'count': result.count}
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'filename="inventory-report.pdf"'
            template = get_template(template_path)
            html = template.render(context)
            pisa_status = pisa.CreatePDF(html, dest=response)
            if pisa_status.err:
                return HttpResponse('Error')
            return response

        if request.method == 'GET':
            query = request.GET.get('q', '')
            if query == '':
                results = Document.objects.filter(complete=True, category__isnull=False, route_id=current_user_id,
                                                  for_release=0).order_by('-id')
            elif query == 'urgent':
                results = Document.objects.filter(urgent=True).order_by('-id')
            elif query == 'mydocs':
                results = Document.objects.filter(route_id=current_user_id).order_by('-id')
            elif query == 'due':
                results = Document.objects.filter(deadline__lte=d).order_by('-id')
            elif query == 'for release':
                results = Document.objects.filter(for_release=1).order_by('-id')
            else:
                results = Document.objects.filter(
                    code__iexact=query) | Document.objects.filter(category__icontains=query) | Document.objects.filter(
                    subject__icontains=query) | Document.objects.filter(
                    sender__icontains=query) | Document.objects.filter(
                    type_id__type_name__icontains=query) | Document.objects.filter(
                    action_taken_id__action_taken__icontains=query) | Document.objects.filter(
                    date_received__icontains=query)| Document.objects.filter(
                    description__icontains=query)

            recount = results.count
            page = request.GET.get('page', 1)
            paginator = Paginator(results, 100)
            try:
                results = paginator.page(page)
            except PageNotAnInteger:
                results = paginator.page(1)
            except EmptyPage:
                results = paginator.page(paginator.num_pages)
            context = {'result': results, 'count': recount, 'dd': d, 'urg': urg.count, 'allcnt': allcnt.count,
                       'due': due.count, 'rel': rel.count, 'current_user_id': current_user_id,
                       'current_user': current_user, 'online_count': online_count.count, 'togo': togo.count,
                       'days_togo': days_togo,'mineres': mineres.count,'acted_rel':acted_rel.count}
            return render(request, 'mydocu_dashboard.html', context)


def division_docs(request):  # view all docs at dashboar or accepted docs
    current_user_id = request.user.id
    current_user = request.user.is_superuser


    current_user_division = User.objects.get(id=current_user_id)
    mineres = Document.objects.filter(complete=True, category__isnull=False, route_id=current_user_id, for_release=0).order_by(
        '-id')
    d = datetime.date.today()
    days_togo = datetime.date.today() + datetime.timedelta(days=1)
    togo = Document.objects.filter(deadline=days_togo)
    allcnt = Document.objects.filter(acted_release=0,for_release=0,complete=True, category__isnull=False,route=current_user_id).order_by('-id')
    allcnt_super = Document.objects.filter(acted_release=0, for_release=0, complete=True,
                                     category__isnull=False).order_by('-id')
    urg = Document.objects.filter(urgent=1)
    due = Document.objects.filter(deadline__lte=d)
    rel = Document.objects.filter(for_release=1,acted_release=0)
    acted_rel = Document.objects.filter(for_release=1,acted_release=1)
    online_count = Document.objects.filter(category__isnull=True, online=True)
    div_res = Document.objects.filter(complete=True, category__isnull=False, acted_release=0, for_release=0,
                                      division=current_user_division.first_name).order_by('-id')


    if 'print' in request.GET:  # determined what button to click
        template_path = 'print_document.html'
        query = request.GET.get('q', '')
        if query == 'online':
            result = Document.objects.filter(online=1,route_id=current_user_id).order_by('-id')
        elif query == '':
            result = Document.objects.filter(complete=True, category__isnull=False,acted_release=0,for_release=0,division=current_user_division.first_name).order_by('-id')
        elif query == 'urgent':
            result = Document.objects.filter(urgent=True,route_id=current_user_id).order_by('-id')
        elif query == 'due':
            result = Document.objects.filter(deadline__lte=d,route_id=current_user_id).order_by('-id')
        elif query == 'for release':
            result = Document.objects.filter(for_release=1,route_id=current_user_id).order_by('-id')
        else:
            result = Document.objects.filter(
                code__iexact=query) | Document.objects.filter(category__icontains=query) | Document.objects.filter(
                subject__icontains=query) | Document.objects.filter(
                sender__icontains=query) | Document.objects.filter(
                date_received__icontains=query) | Document.objects.filter(
                description__icontains=query)

        context = {'result': result, 'count': result.count}
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'filename="inventory-report.pdf"'
        template = get_template(template_path)
        html = template.render(context)
        pisa_status = pisa.CreatePDF(html, dest=response)
        if pisa_status.err:
            return HttpResponse('Error')
        return response

    if request.method == 'GET':
        query = request.GET.get('q', '')
        if query == '':
            results = Document.objects.filter(complete=True, category__isnull=False,acted_release=0,for_release=0,division=current_user_division.first_name).order_by('-id')
        elif query == 'urgent':
            results = Document.objects.filter(urgent=True).order_by('-id')
        elif query == 'mydocs':
            results = Document.objects.filter(route_id=current_user_id).order_by('-id')
        elif query == 'due':
            results = Document.objects.filter(deadline__lte=d).order_by('-id')
        elif query == 'for release':
            results = Document.objects.filter(for_release=1).order_by('-id')
        else:
            results = Document.objects.filter(
                code__iexact=query) | Document.objects.filter(category__icontains=query) | Document.objects.filter(
                subject__icontains=query) | Document.objects.filter(
                sender__icontains=query) | Document.objects.filter(
                type_id__type_name__icontains=query) | Document.objects.filter(
                action_taken_id__action_taken__icontains=query) | Document.objects.filter(
                date_received__icontains=query)| Document.objects.filter(
                description__icontains=query)

        recount = results.count
        page = request.GET.get('page', 1)
        paginator = Paginator(results, 100)
        try:
            results = paginator.page(page)
        except PageNotAnInteger:
            results = paginator.page(1)
        except EmptyPage:
            results = paginator.page(paginator.num_pages)
        context = {'result': results, 'count': recount, 'dd': d, 'urg': urg.count, 'allcnt': allcnt.count,
                   'due': due.count, 'rel': rel.count, 'current_user_id': current_user_id,
                   'current_user': current_user, 'online_count': online_count.count, 'togo': togo.count,'allcnt_super':allcnt_super.count,
                   'days_togo': days_togo,'mineres': mineres.count,'acted_rel':acted_rel.count,'div_res':div_res.count }
        return render(request, 'division_dashboard.html', context)

def urgent_docs(request):
    current_user_id = request.user.id
    current_user = request.user.is_superuser
    # mineres = Document.objects.filter(complete=True, category__isnull=False, route_id=current_user_id).order_by('-id')
    d = datetime.date.today()
    days_togo = datetime.date.today() + datetime.timedelta(days=1)
    togo = Document.objects.filter(deadline=days_togo, route_id=current_user_id)
    allcnt = Document.objects.filter(acted_release=0,for_release=0,complete=True, category__isnull=False,route_id=current_user_id).order_by('-id')
    allcnt_super = Document.objects.filter(acted_release=0, for_release=0, complete=True, category__isnull=False).order_by('-id')
    urg = Document.objects.filter(urgent=1, route_id=current_user_id)
    urg_super = Document.objects.filter(urgent=1)
    due = Document.objects.filter(deadline__lte=d, route_id=current_user_id)
    rel = Document.objects.filter(for_release=1, acted_release=0)
    online_count = Document.objects.filter(category__isnull=True, online=True)
    multir = Document.objects.filter(complete=True, category__isnull=False, multiple_route=True).order_by('-id')
    acted_rel = Document.objects.filter(for_release=1, acted_release=1, )

    if 'print' in request.GET:  # determined what button to click
        template_path = 'print_document.html'
        query = request.GET.get('q', '')

        if query == '':
            if current_user:
                result = Document.objects.filter(urgent=True).order_by('-id')
            else:
                result = Document.objects.filter(urgent=True,route=current_user_id).order_by('-id')
        elif query == '':
            result = Document.objects.filter(route_id=current_user_id,for_release=1).order_by('-id')
        elif query == 'urgent':
            result = Document.objects.filter(urgent=True,for_release=1).order_by('-id')
        elif query == 'due':
            result = Document.objects.filter(deadline__lte=d,for_release=1).order_by('-id')
        elif query == 'for release':
            result = Document.objects.filter(route_id=current_user_id,for_release=1).order_by('-id')
        else:
            result = Document.objects.filter(
                code__iexact=query) | Document.objects.filter(category__icontains=query) | Document.objects.filter(
                subject__icontains=query) | Document.objects.filter(
                sender__icontains=query) | Document.objects.filter(
                type_id__type_name__icontains=query) | Document.objects.filter(
                action_taken_id__action_taken__icontains=query) | Document.objects.filter(
                date_received__icontains=query) | Document.objects.filter(
                description__icontains=query)

        context = {'result': result, 'count': result.count}
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'filename="inventory-report.pdf"'
        template = get_template(template_path)
        html = template.render(context)
        pisa_status = pisa.CreatePDF(html, dest=response)
        if pisa_status.err:
            return HttpResponse('Error')
        return response

    if request.method == 'GET':
        query = request.GET.get('q', '')
        if query == '':
            if current_user:
                results = Document.objects.filter(urgent=True).order_by('-id')
            else:
                results = Document.objects.filter(urgent=True,route=current_user_id).order_by('-id')
        else:
            results = Document.objects.filter(
            code__iexact=query) | Document.objects.filter(category__icontains=query) | Document.objects.filter(
            subject__icontains=query) | Document.objects.filter(
            sender__icontains=query) | Document.objects.filter(
            type_id__type_name__icontains=query) | Document.objects.filter(
            action_taken_id__action_taken__icontains=query) | Document.objects.filter(
            date_received__icontains=query) | Document.objects.filter(
            description__icontains=query)

        recount = results.count
        page = request.GET.get('page', 1)
        paginator = Paginator(results, 100)
        try:
            results = paginator.page(page)
        except PageNotAnInteger:
            results = paginator.page(1)
        except EmptyPage:
            results = paginator.page(paginator.num_pages)
        context = {'result': results, 'count': recount, 'dd': d, 'urg': urg.count, 'allcnt': allcnt.count,
                   'current_user_id': current_user_id, 'current_user': current_user,'urg_super':urg_super.count,
                   'online_count': online_count.count, 'togo': togo.count, 'days_togo': days_togo,
                   'due': due.count, 'rel': rel.count, 'multir': multir.count, 'acted_rel': acted_rel.count,'allcnt_super':allcnt_super.count}
        return render(request, 'urgent_dashboard.html', context)

def acted_release_docs(request):
    current_user_id = request.user.id
    current_user = request.user.is_superuser
    # mineres = Document.objects.filter(complete=True, category__isnull=False, route_id=current_user_id).order_by('-id')
    d = datetime.date.today()
    days_togo = datetime.date.today() + datetime.timedelta(days=1)
    togo = Document.objects.filter(deadline=days_togo, route_id=current_user_id)
    allcnt = Document.objects.filter(acted_release=0,for_release=0,complete=True, category__isnull=False,route_id=current_user_id).order_by('-id')
    allcnt_super = Document.objects.filter(acted_release=0, for_release=0, complete=True, category__isnull=False).order_by('-id')
    urg = Document.objects.filter(urgent=1, route_id=current_user_id)
    urg_super = Document.objects.filter(urgent=1)
    due = Document.objects.filter(deadline__lte=d, route_id=current_user_id)
    rel = Document.objects.filter(for_release=1, acted_release=0)
    online_count = Document.objects.filter(category__isnull=True, online=True)
    multir = Document.objects.filter(complete=True, category__isnull=False, multiple_route=True).order_by('-id')
    acted_rel = Document.objects.filter(for_release=1, acted_release=1, )

    if 'print' in request.GET:  # determined what button to click
        template_path = 'print_document.html'
        query = request.GET.get('q', '')

        if query == '':
            result = Document.objects.filter(for_release=1,acted_release=1).order_by('-id')
        elif query == '':
            result = Document.objects.filter(route_id=current_user_id,for_release=1).order_by('-id')
        elif query == 'urgent':
            result = Document.objects.filter(urgent=True,for_release=1).order_by('-id')
        elif query == 'due':
            result = Document.objects.filter(deadline__lte=d,for_release=1).order_by('-id')
        elif query == 'for release':
            result = Document.objects.filter(route_id=current_user_id,for_release=1).order_by('-id')
        else:
            result = Document.objects.filter(
                code__iexact=query) | Document.objects.filter(category__icontains=query) | Document.objects.filter(
                subject__icontains=query) | Document.objects.filter(
                sender__icontains=query) | Document.objects.filter(
                date_received__icontains=query) | Document.objects.filter(
                description__icontains=query)

        context = {'result': result, 'count': result.count}
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'filename="inventory-report.pdf"'
        template = get_template(template_path)
        html = template.render(context)
        pisa_status = pisa.CreatePDF(html, dest=response)
        if pisa_status.err:
            return HttpResponse('Error')
        return response

    if request.method == 'GET':
        query = request.GET.get('q', '')
        if query == '':
            results = Document.objects.filter(for_release=1,acted_release=1).order_by('-id')

        else:
            results = Document.objects.filter(
            code__iexact=query) | Document.objects.filter(category__icontains=query) | Document.objects.filter(
            subject__icontains=query) | Document.objects.filter(
            sender__icontains=query) | Document.objects.filter(
            type_id__type_name__icontains=query) | Document.objects.filter(
            action_taken_id__action_taken__icontains=query) | Document.objects.filter(
            date_received__icontains=query) | Document.objects.filter(
            description__icontains=query)

        recount = results.count
        page = request.GET.get('page', 1)
        paginator = Paginator(results, 500)
        try:
            results = paginator.page(page)
        except PageNotAnInteger:
            results = paginator.page(1)
        except EmptyPage:
            results = paginator.page(paginator.num_pages)
        context = {'result': results, 'count': recount, 'dd': d, 'urg': urg.count, 'allcnt': allcnt.count,
                   'current_user_id': current_user_id, 'current_user': current_user,'urg_super':urg_super.count,
                   'online_count': online_count.count, 'togo': togo.count, 'days_togo': days_togo,
                   'due': due.count, 'rel': rel.count, 'multir': multir.count, 'acted_rel': acted_rel.count,'allcnt_super':allcnt_super.count}
        return render(request, 'acted_release_dashboard.html', context)

def due_docs(request):
    current_user_id = request.user.id
    current_user = request.user.is_superuser
    # mineres = Document.objects.filter(complete=True, category__isnull=False, route_id=current_user_id).order_by('-id')
    d = datetime.date.today()
    days_togo = datetime.date.today() + datetime.timedelta(days=1)
    togo = Document.objects.filter(deadline=days_togo, route_id=current_user_id)
    allcnt = Document.objects.filter(acted_release=0,for_release=0,complete=True, category__isnull=False,route_id=current_user_id).order_by('-id')
    allcnt_super = Document.objects.filter(acted_release=0, for_release=0, complete=True, category__isnull=False).order_by('-id')
    urg = Document.objects.filter(urgent=1, route_id=current_user_id)
    urg_super = Document.objects.filter(urgent=1)
    due = Document.objects.filter(deadline__lte=d, route_id=current_user_id,for_release=0)
    due_super = Document.objects.filter(deadline__lte=d,for_release=0)
    rel = Document.objects.filter(for_release=1, acted_release=0)
    online_count = Document.objects.filter(category__isnull=True, online=True)
    multir = Document.objects.filter(complete=True, category__isnull=False, multiple_route=True).order_by('-id')
    acted_rel = Document.objects.filter(for_release=1, acted_release=1, )

    if 'print' in request.GET:  # determined what button to click
        template_path = 'print_document.html'
        query = request.GET.get('q', '')

        if query == '':
            if current_user:
                result = Document.objects.filter(deadline__lte=d,for_release=0).order_by('-id')
            else:
                result = Document.objects.filter(deadline__lte=d,for_release=0, route_id=current_user_id).order_by('-id')

        elif query == '':
            result = Document.objects.filter(route_id=current_user_id,for_release=1).order_by('-id')
        elif query == 'urgent':
            result = Document.objects.filter(urgent=True,for_release=1).order_by('-id')
        elif query == 'due':
            result = Document.objects.filter(deadline__lte=d,for_release=1).order_by('-id')
        elif query == 'for release':
            result = Document.objects.filter(route_id=current_user_id,for_release=1).order_by('-id')
        else:
            result = Document.objects.filter(
                code__iexact=query) | Document.objects.filter(category__icontains=query) | Document.objects.filter(
                subject__icontains=query) | Document.objects.filter(
                sender__icontains=query) | Document.objects.filter(
                type_id__type_name__icontains=query) | Document.objects.filter(
                action_taken_id__action_taken__icontains=query) | Document.objects.filter(
                date_received__icontains=query) | Document.objects.filter(
                description__icontains=query)

        context = {'result': result, 'count': result.count}
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'filename="inventory-report.pdf"'
        template = get_template(template_path)
        html = template.render(context)
        pisa_status = pisa.CreatePDF(html, dest=response)
        if pisa_status.err:
            return HttpResponse('Error')
        return response

    if request.method == 'GET':
        query = request.GET.get('q', '')
        if query == '':
            if current_user:
                results = Document.objects.filter(deadline__lte=d, for_release=0).order_by('-id')
            else:
                results = Document.objects.filter(deadline__lte=d, for_release=0, route_id=current_user_id).order_by('-id')

        else:
            results = Document.objects.filter(
            code__iexact=query) | Document.objects.filter(category__icontains=query) | Document.objects.filter(
            subject__icontains=query) | Document.objects.filter(
            sender__icontains=query) | Document.objects.filter(
            type_id__type_name__icontains=query) | Document.objects.filter(
            action_taken_id__action_taken__icontains=query) | Document.objects.filter(
            date_received__icontains=query) | Document.objects.filter(
            description__icontains=query)

        recount = results.count
        page = request.GET.get('page', 1)
        paginator = Paginator(results, 100)
        try:
            results = paginator.page(page)
        except PageNotAnInteger:
            results = paginator.page(1)
        except EmptyPage:
            results = paginator.page(paginator.num_pages)
        context = {'result': results, 'count': recount, 'dd': d, 'urg': urg.count, 'allcnt': allcnt.count,
                   'current_user_id': current_user_id, 'current_user': current_user,'urg_super':urg_super.count,
                   'online_count': online_count.count, 'togo': togo.count, 'days_togo': days_togo,'due_super':due_super.count,
                   'due': due.count, 'rel': rel.count, 'multir': multir.count, 'acted_rel': acted_rel.count,'allcnt_super':allcnt_super.count,'userN':'RD_Carido'}
        return render(request, 'due_dashboard.html', context)

def to_due_docs(request):
    current_user_id = request.user.id
    current_user = request.user.is_superuser
    # mineres = Document.objects.filter(complete=True, category__isnull=False, route_id=current_user_id).order_by('-id')
    d = datetime.date.today()
    days_togo = datetime.date.today() + datetime.timedelta(days=1)
    togo = Document.objects.filter(deadline=days_togo, route_id=current_user_id)
    allcnt = Document.objects.filter(acted_release=0,for_release=0,complete=True, category__isnull=False,route_id=current_user_id).order_by('-id')
    allcnt_super = Document.objects.filter(acted_release=0, for_release=0, complete=True, category__isnull=False).order_by('-id')
    urg = Document.objects.filter(urgent=1, route_id=current_user_id)
    urg_super = Document.objects.filter(urgent=1)
    due = Document.objects.filter(deadline__lte=d, route_id=current_user_id)
    due_super = Document.objects.filter(deadline__lte=d)
    rel = Document.objects.filter(for_release=1, acted_release=0)
    online_count = Document.objects.filter(category__isnull=True, online=True)
    multir = Document.objects.filter(complete=True, category__isnull=False, multiple_route=True).order_by('-id')
    acted_rel = Document.objects.filter(for_release=1, acted_release=1, )

    if 'print' in request.GET:  # determined what button to click
        template_path = 'print_document.html'
        query = request.GET.get('q', '')

        if query == '':
            if current_user:
                result = Document.objects.filter(deadline=days_togo).order_by('-id')
            else:
                result = Document.objects.filter(deadline=days_togo, route_id=current_user_id).order_by('-id')

        elif query == '':
            result = Document.objects.filter(route_id=current_user_id,for_release=1).order_by('-id')
        elif query == 'urgent':
            result = Document.objects.filter(urgent=True,for_release=1).order_by('-id')
        elif query == 'due':
            result = Document.objects.filter(deadline__lte=d,for_release=1).order_by('-id')
        elif query == 'for release':
            result = Document.objects.filter(route_id=current_user_id,for_release=1).order_by('-id')
        else:
            result = Document.objects.filter(
                code__iexact=query) | Document.objects.filter(category__icontains=query) | Document.objects.filter(
                subject__icontains=query) | Document.objects.filter(
                sender__icontains=query) | Document.objects.filter(
                type_id__type_name__icontains=query) | Document.objects.filter(
                action_taken_id__action_taken__icontains=query) | Document.objects.filter(
                date_received__icontains=query) | Document.objects.filter(
                description__icontains=query)

        context = {'result': result, 'count': result.count}
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'filename="inventory-report.pdf"'
        template = get_template(template_path)
        html = template.render(context)
        pisa_status = pisa.CreatePDF(html, dest=response)
        if pisa_status.err:
            return HttpResponse('Error')
        return response

    if request.method == 'GET':
        query = request.GET.get('q', '')
        if query == '':
            if current_user:
                results = Document.objects.filter(deadline=days_togo).order_by('-id')
            else:
                results = Document.objects.filter(deadline=days_togo, route_id=current_user_id).order_by('-id')

        else:
            results = Document.objects.filter(
            code__iexact=query) | Document.objects.filter(category__icontains=query) | Document.objects.filter(
            subject__icontains=query) | Document.objects.filter(
            sender__icontains=query) | Document.objects.filter(
            type_id__type_name__icontains=query) | Document.objects.filter(
            action_taken_id__action_taken__icontains=query) | Document.objects.filter(
            date_received__icontains=query) | Document.objects.filter(
            description__icontains=query)

        recount = results.count
        page = request.GET.get('page', 1)
        paginator = Paginator(results, 10)
        try:
            results = paginator.page(page)
        except PageNotAnInteger:
            results = paginator.page(1)
        except EmptyPage:
            results = paginator.page(paginator.num_pages)
        context = {'result': results, 'count': recount, 'dd': d, 'urg': urg.count, 'allcnt': allcnt.count,
                   'current_user_id': current_user_id, 'current_user': current_user,'urg_super':urg_super.count,
                   'online_count': online_count.count, 'togo': togo.count, 'days_togo': days_togo,'due_super':due_super.count,
                   'due': due.count, 'rel': rel.count, 'multir': multir.count, 'acted_rel': acted_rel.count,'allcnt_super':allcnt_super.count}
        return render(request, 'to_due_dashboard.html', context)

def all_due_docs(request):
    current_user_id = request.user.id
    current_user = request.user.is_superuser
    # mineres = Document.objects.filter(complete=True, category__isnull=False, route_id=current_user_id).order_by('-id')
    d = datetime.date.today()
    days_togo = datetime.date.today() + datetime.timedelta(days=1)
    togo = Document.objects.filter(deadline=days_togo, route_id=current_user_id)
    allcnt = Document.objects.filter(acted_release=0,for_release=0,complete=True, category__isnull=False,route_id=current_user_id).order_by('-id')
    allcnt_super = Document.objects.filter(acted_release=0, for_release=0, complete=True, category__isnull=False).order_by('-id')
    urg = Document.objects.filter(urgent=1, route_id=current_user_id)
    urg_super = Document.objects.filter(urgent=1)
    due = Document.objects.filter(deadline__lte=d, route_id=current_user_id,for_release=0)
    due_super = Document.objects.filter(deadline__lte=d,for_release=0)
    rel = Document.objects.filter(for_release=1, acted_release=0)
    online_count = Document.objects.filter(category__isnull=True, online=True)
    multir = Document.objects.filter(complete=True, category__isnull=False, multiple_route=True).order_by('-id')
    acted_rel = Document.objects.filter(for_release=1, acted_release=1, )

    if 'print' in request.GET:  # determined what button to click
        template_path = 'print_document.html'
        query = request.GET.get('q', '')

        if query == '':

            result = Document.objects.filter(deadline__lte=d,for_release=0).order_by('-id')

        elif query == '':
            result = Document.objects.filter(route_id=current_user_id,for_release=1).order_by('-id')
        elif query == 'urgent':
            result = Document.objects.filter(urgent=True,for_release=1).order_by('-id')
        elif query == 'due':
            result = Document.objects.filter(deadline__lte=d,for_release=1).order_by('-id')
        elif query == 'for release':
            result = Document.objects.filter(route_id=current_user_id,for_release=1).order_by('-id')
        else:
            result = Document.objects.filter(
                code__iexact=query) | Document.objects.filter(category__icontains=query) | Document.objects.filter(
                subject__icontains=query) | Document.objects.filter(
                sender__icontains=query) | Document.objects.filter(
                type_id__type_name__icontains=query) | Document.objects.filter(
                action_taken_id__action_taken__icontains=query) | Document.objects.filter(
                date_received__icontains=query) | Document.objects.filter(
                description__icontains=query)

        context = {'result': result, 'count': result.count}
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'filename="inventory-report.pdf"'
        template = get_template(template_path)
        html = template.render(context)
        pisa_status = pisa.CreatePDF(html, dest=response)
        if pisa_status.err:
            return HttpResponse('Error')
        return response

    if request.method == 'GET':
        query = request.GET.get('q', '')
        if query == '':

            results = Document.objects.filter(deadline__lte=d, for_release=0).order_by('-id')

        else:
            results = Document.objects.filter(
            code__iexact=query) | Document.objects.filter(category__icontains=query) | Document.objects.filter(
            subject__icontains=query) | Document.objects.filter(
            sender__icontains=query) | Document.objects.filter(
            type_id__type_name__icontains=query) | Document.objects.filter(
            action_taken_id__action_taken__icontains=query) | Document.objects.filter(
            date_received__icontains=query) | Document.objects.filter(
            description__icontains=query)

        recount = results.count
        page = request.GET.get('page', 1)
        paginator = Paginator(results, 100)
        try:
            results = paginator.page(page)
        except PageNotAnInteger:
            results = paginator.page(1)
        except EmptyPage:
            results = paginator.page(paginator.num_pages)
        context = {'result': results, 'count': recount, 'dd': d, 'urg': urg.count, 'allcnt': allcnt.count,
                   'current_user_id': current_user_id, 'current_user': current_user,'urg_super':urg_super.count,
                   'online_count': online_count.count, 'togo': togo.count, 'days_togo': days_togo,'due_super':due_super.count,
                   'due': due.count, 'rel': rel.count, 'multir': multir.count, 'acted_rel': acted_rel.count,'allcnt_super':allcnt_super.count,'userN':'RD_Carido'}
        return render(request, 'all_due_docs.html', context)

def outgoing(request):
    if request.method == 'GET':
        query = request.GET.get('q', '')
        if query == '':
            results = Outgoing.objects.all().order_by('-id')
        else:
            results = Outgoing.objects.filter(
                doc_code__iexact=query) | Outgoing.objects.filter(
                subject__icontains=query) | Outgoing.objects.filter(
                doc_from__icontains=query) | Outgoing.objects.filter(
                doc_to__icontains=query) | Outgoing.objects.filter(
                doc_type__icontains=query)


        page = request.GET.get('page', 1)
        paginator = Paginator(results, 20)
        try:
            results = paginator.page(page)
        except PageNotAnInteger:
            results = paginator.page(1)
        except EmptyPage:
            results = paginator.page(paginator.num_pages)
        context = {'results': results}
        return render(request, 'outgoing.html',context)


def add_outgoing(request):  # add docs outgoing
    form = OutgoingForm()
    if request.method == 'POST':
        #form = OutgoingForm(request.POST, request.FILES)
        form = OutgoingForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('outgoing')
    context = {'form': form}
    return render(request, 'add_outgoing.html', context)

def detailed_copyfurnish(request,pk):
    result = Document.objects.filter(code=pk)
    context ={'result':result}
    return render(request, 'detailed_copyfurnish.html', context)

