from django.forms import ModelForm
from .models import Document,Types,ActionTaken,Outgoing,User

class AddDocumentForm(ModelForm):
    def __init__(self,*args,**kwargs):
        super(AddDocumentForm,self).__init__(*args,**kwargs)
        self.fields['code'].widget.attrs['readonly']=True

    class Meta:

        model = Document
        #fields = '__all__'
        fields = ['code','type','category','subject','description','sender','contact','deadline',
                    'pdf_file','route'
                 ]
        labels = {
            "contact": "Contact No.",
            "deadline": "Deadline (YYYY-MM-DD)",
            "route": "Route to",
            "description": "Attachments",
        }


class AddOnlineDocumentForm(ModelForm):
    class Meta:

        model = Document
        #fields = '__all__'
        fields = ['type','subject','description','sender','contact','pdf_file'
                 ]

class ReuploadOnlineDocumentForm(ModelForm):
    class Meta:

        model = Document
        #fields = '__all__'
        fields = ['pdf_file']

class DenyOnlineDocumentForm(ModelForm):
    class Meta:

        model = Document
        #fields = '__all__'
        fields = ['remark']

class AcceptDocumentForm(ModelForm):
    def __init__(self,*args,**kwargs):
        super(AcceptDocumentForm,self).__init__(*args,**kwargs)
        self.fields['code'].widget.attrs['readonly']=True

    class Meta:
        model = Document
        #fields = '__all__'
        fields = ['code','type','category','subject','description','sender','contact','deadline',
                    'route'
                 ]

class EditDocumentForm(ModelForm):

    def __init__(self,*args,**kwargs):
        super(EditDocumentForm,self).__init__(*args,**kwargs)
        self.fields['code'].widget.attrs['readonly']=True

    class Meta:

        model = Document
        #fields = '__all__'
        fields = ['code','type','category','subject','description','sender','contact','deadline',
                    'multiple_route','urgent','pdf_file'
                 ]

class RouteDocumentForm(ModelForm):

    def __init__(self,*args,**kwargs):
        super(RouteDocumentForm,self).__init__(*args,**kwargs)
        self.fields['code'].widget.attrs['readonly']=True

    def __init__(self, *args, **kwargs):
        super(RouteDocumentForm, self).__init__(*args, **kwargs)
        self.user = kwargs.pop('user', None)
        self.fields['route'].queryset = self.fields['route'].queryset.filter(is_active=True).order_by('username')
        self.fields['action_taken'].queryset = self.fields['action_taken'].queryset.order_by('action_taken')

    class Meta:
        model = Document
        #fields = '__all__'
        fields = ['code','deadline','multiple_route','urgent','route','action_taken','for_release','acted_release', 'confidential'
                 ]

        labels = {
            "for_release": "Acted",
            "acted_release": "For Release",
        }


class TypeForm(ModelForm):
    class Meta:
        model = Types
        #fields = '__all__'
        fields = ['type_name']

class TypeActionForm(ModelForm):
    class Meta:
        model = ActionTaken
        #fields = '__all__'
        fields = ['action_taken']



class SendApprovedDocumentForm(ModelForm):

    def __init__(self,*args,**kwargs):
        super(SendApprovedDocumentForm,self).__init__(*args,**kwargs)
        self.fields['code'].widget.attrs['readonly']=True
        self.fields['sender'].label = "Send to"
        self.fields['sender'].widget.attrs['readonly'] = True

    class Meta:


        model = Document
        #fields = '__all__'
        fields = ['code','send_file','sender']


class Edit_TypeForm(ModelForm):
    class Meta:
        model = Types
        #fields = '__all__'
        fields = ['type_name']

class Edit_TypeActionForm(ModelForm):
    class Meta:
        model = ActionTaken
        #fields = '__all__'
        fields = ['action_taken']

class OutgoingForm(ModelForm):
    class Meta:
        model = Outgoing
        fields = ['doc_code','doc_to','doc_from','doc_type','subject']
        #exclude = ['attach_file']

        labels = {
            "doc_code": "Document Code",
            "doc_to": "Document To",
            "doc_from": "Document From",
            "doc_type": "Document Type",

        }

