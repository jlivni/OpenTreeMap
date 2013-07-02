from django import forms
from models import Tree, Plot, Species, TreePhoto, TreeAlert, TreeFauna, TreeAction, Neighborhood, ZipCode, ImportEvent, Choices, status_choices
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.localflavor.us.forms import USZipCodeField
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from datetime import datetime
import math

class SendInfoForm(forms.Form):
    name = forms.CharField(max_length=100, 
           help_text="Full Name", widget=forms.TextInput(attrs={'size':'40'}),required=False)
    sender = forms.EmailField(
              help_text="Your email address", widget=forms.TextInput(attrs={'size':'40'}),required=True)

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, 
           help_text="Full Name", widget=forms.TextInput(attrs={'size':'40'}),required=False)
    subject = forms.CharField(max_length=100, 
              help_text="Subject of your message", widget=forms.TextInput(attrs={'size':'40'}))
    sender = forms.EmailField(
              help_text="Your email address", widget=forms.TextInput(attrs={'size':'40'}),required=True)
    message = forms.CharField(
              help_text="Please enter as much text as you would like", 
              widget=forms.Textarea(attrs={'rows':'12','cols':'60'}))
    cc_myself = forms.BooleanField(required=False, 
                help_text="Send yourself a copy of this message")
                
class TreeEditPhotoForm(forms.ModelForm):
    class Meta:
        model = TreePhoto
        exclude = ('reported_by',)
        fields = ('title','photo',)

class TreeAddForm(forms.Form):
    edit_address_street = forms.CharField(max_length=200, required=True, initial="Enter an Address or Intersection")
    geocode_address = forms.CharField(widget=forms.HiddenInput, max_length=255, required=True)
    edit_address_city = forms.CharField(max_length=100, required=False, initial="Enter a City")
    edit_latitude = forms.CharField(max_length=100, required=False, initial="Latitude")
    edit_longitude = forms.CharField(max_length=100, required=False, initial="Longitude")
    edit_address_zip = USZipCodeField(widget=forms.HiddenInput, required=False)
    lat = forms.FloatField(widget=forms.HiddenInput,required=True)
    lon = forms.FloatField(widget=forms.HiddenInput,required=True)
    species_name = forms.CharField(required=False, initial="Enter a Species Name")
    species_id = forms.CharField(widget=forms.HiddenInput, required=False)
    dbh = forms.FloatField(required=False, label="Trunk size")
    crown_width = forms.FloatField(required=False, label="Crown Diameter")
    dbh_type = forms.ChoiceField(required=False, widget=forms.RadioSelect, choices=[('diameter', 'Diameter'), ('circumference', 'Circumference')])
    height = forms.FloatField(required=False, label="Tree height")
    canopy_height = forms.IntegerField(required=False)
    plot_width = forms.ChoiceField(required=False, label="Enter the planting site length", choices=[('1','1'),('2','2'),('3','3'),('4','4'),('5','5'),('6','6'),('7','7'),('8','8'),('9','9'),('10','10'),('11','11'),('12','12'),('13','13'),('14','14'),('15','15'),('99','15+')])
    plot_length = forms.ChoiceField(required=False, label="Enter the planting site width", choices=[('1','1'),('2','2'),('3','3'),('4','4'),('5','5'),('6','6'),('7','7'),('8','8'),('9','9'),('10','10'),('11','11'),('12','12'),('13','13'),('14','14'),('15','15'),('99','15+')])
    plot_width_in = forms.ChoiceField(required=False, choices=[('1','1'),('2','2'),('3','3'),('4','4'),('5','5'),('6','6'),('7','7'),('8','8'),('9','9'),('10','10'),('11','11')])
    plot_length_in = forms.ChoiceField(required=False, choices=[('1','1'),('2','2'),('3','3'),('4','4'),('5','5'),('6','6'),('7','7'),('8','8'),('9','9'),('10','10'),('11','11')])
    plot_type = forms.TypedChoiceField(choices=Choices().get_field_choices('plot_type'), required=False)
    power_lines = forms.TypedChoiceField(choices=Choices().get_field_choices('powerline_conflict_potential'), required=False)
    sidewalk_damage = forms.ChoiceField(choices=Choices().get_field_choices('sidewalk_damage'), required=False)
    condition = forms.ChoiceField(choices=Choices().get_field_choices('condition'), required=False)
    canopy_condition = forms.ChoiceField(choices=Choices().get_field_choices('canopy_condition'), required=False)
    fauna = forms.MultipleChoiceField(choices=Choices().get_field_choices('fauna'), required=False, widget=forms.CheckboxSelectMultiple)
    target = forms.ChoiceField(required=False, choices=[('add', 'I want to add another tree'), ('edit', 'I\'m done!')], initial='edit', widget=forms.RadioSelect)        

    def __init__(self, *args, **kwargs):
        super(TreeAddForm, self).__init__(*args, **kwargs)
        if not self.fields['plot_type'].choices[0][0] == '':        
            self.fields['plot_type'].choices.insert(0, ('','Select One...' ) )
            self.fields['power_lines'].choices.insert(0, ('','Select One...' ) )
            self.fields['sidewalk_damage'].choices.insert(0, ('','Select One...' ) )
            self.fields['condition'].choices.insert(0, ('','Select One...' ) )
            self.fields['canopy_condition'].choices.insert(0, ('','Select One...' ) )
            self.fields['plot_width'].choices.insert(0, ('','Select Feet...' ) )
            self.fields['plot_width_in'].choices.insert(0, ('','Select Inches...' ) )
            self.fields['plot_length'].choices.insert(0, ('','Select Feet...' ) )
            self.fields['plot_length_in'].choices.insert(0, ('','Select Inches...' ) )


    def clean(self):        
        cleaned_data = self.cleaned_data 
        height = cleaned_data.get('height')
        canopy_height = cleaned_data.get('canopy_height') 
        try:
            point = Point(cleaned_data.get('lon'),cleaned_data.get('lat'),srid=4326)  
            nbhood = Neighborhood.objects.filter(geometry__contains=point)
        except:
            raise forms.ValidationError("This tree is missing a location. Enter an address in Step 1 and update the map to add a location for this tree.") 
        
        if nbhood.count() < 1:
            raise forms.ValidationError("The selected location is outside our area. Please specify a location within the " + settings.REGION_NAME + " region.")
        
        if height > 300:
            raise forms.ValidationError("Height is too large.")
        if canopy_height > 300:
            raise forms.ValidationError("Canopy height is too large.")

        if canopy_height and height and canopy_height > height:
            raise forms.ValidationError("Canopy height cannot be larger than tree height.")
            

        return cleaned_data 
        
    def save(self,request):
        from django.contrib.gis.geos import Point

        plot = Plot()
        plot.data_owner = request.user

        address = self.cleaned_data.get('edit_address_street')
        if address:
            plot.address_street = address
            plot.geocoded_address = address
        city = self.cleaned_data.get('edit_address_city')
        geo_address = self.cleaned_data.get('geocode_address')
        if geo_address:
            plot.geocoded_address = geo_address
        if city:
            plot.address_city = city
        zip_ = self.cleaned_data.get('edit_address_zip')
        if zip_:
            plot.address_zip = zip_
        
        plot_width = self.cleaned_data.get('plot_width')
        plot_width_in = self.cleaned_data.get('plot_width_in')
        if plot_width:
            plot.width = float(plot_width)
        if plot_width_in:
            plot.width = plot.width + (float(plot_width_in) / 12)
        plot_length = self.cleaned_data.get('plot_length')
        plot_length_in = self.cleaned_data.get('plot_length_in')
        if plot_length:
            plot.length = float(plot_length)
        if plot_length_in:
            plot.length = plot.length + (float(plot_length_in) / 12)
        plot_type = self.cleaned_data.get('plot_type')
        if plot_type:
            plot.type = plot_type
        power_lines = self.cleaned_data.get('power_lines')
        if power_lines != "":
            plot.powerline_conflict_potential = power_lines
        sidewalk_damage = self.cleaned_data.get('sidewalk_damage')
        if sidewalk_damage:
            plot.sidewalk_damage = sidewalk_damage

        import_event, created = ImportEvent.objects.get_or_create(file_name='site_add',)
        plot.import_event = import_event

        pnt = Point(self.cleaned_data.get('lon'),self.cleaned_data.get('lat'),srid=4326)
        plot.geometry = pnt
        plot.last_updated_by = request.user
        plot.save()

        species = self.cleaned_data.get('species_id')
        height = self.cleaned_data.get('height')
        canopy_height = self.cleaned_data.get('canopy_height')
        dbh = self.cleaned_data.get('dbh')
        crown_width = self.cleaned_data.get('crown_width')
        dbh_type = self.cleaned_data.get('dbh_type')
        condition = self.cleaned_data.get('condition')
        canopy_condition = self.cleaned_data.get('canopy_condition')

        new_tree = Tree()
        if species:
            spp = Species.objects.filter(symbol=species)
            if spp:
              new_tree.species=spp[0]

        if crown_width:
            new_tree.crown_width = crown_width
        if height:
            new_tree.height = height
        if canopy_height:
            new_tree.canopy_height = canopy_height
        if dbh:
            if dbh_type == 'circumference':
                dbh = dbh / math.pi
            new_tree.dbh = dbh
        if condition:
            new_tree.condition = condition
        if canopy_condition:
            new_tree.canopy_condition = canopy_condition
        
        new_tree.import_event = import_event            
        new_tree.last_updated_by = request.user
        new_tree.plot = plot
        new_tree.save()
        #print new_tree.__dict__
        fauna = self.cleaned_data.get('fauna')
        if fauna:
            print 'fauna',fauna
            fauna_dict = dict(Choices().get_field_choices('fauna'))
            for f in fauna:
              fauna = TreeFauna()
              fauna.reported_by = request.user
              fauna.key = f
              fauna.value = datetime.now()
              fauna.fauna = fauna_dict[f] # or random string
              fauna.tree = new_tree
              fauna.save()
        
        return plot
     
