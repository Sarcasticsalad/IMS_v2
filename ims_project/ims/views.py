from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Product, Category, Customer, Supplier
from django.http import Http404
from django.urls import reverse
from ims.models import Category, Supplier

# CRUD Helper function to map model names to MongoDB model classes
def get_model_instance(model_name):
    model_classes = {
        'product': Product,
        'category': Category,
        'customer': Customer,
        'supplier': Supplier
    }
    model_class = model_classes.get(model_name.lower())  # Convert to lowercase to match your model naming
    if model_class:
        return model_class
    else:
        raise Http404(f"Model '{model_name}' does not exist.")  
@login_required
def dashboard(request):
    # Render the dashboard page for authenticated users
    return render(request, 'ims/dashboard.html')

@login_required
def model_list(request, model_name):
    try:
        model = get_model_instance(model_name)
        model_instance = model()
        items = model_instance.all()
        return render(request, f'ims/{model_name}/{model_name}_list.html', {'items': items})
    except Http404:
        return render(request, 'ims/404.html')  

@login_required
def model_create(request, model_name):
    try:
        model_class = get_model_instance(model_name)
        model_instance = model_class()

        if request.method == 'POST':
            data = request.POST.dict()
            data.pop('csrfmiddlewaretoken', None)

            image_file = request.FILES.get('image')

            if model_name == 'product' and image_file:
                model_instance.create(data, image_file=image_file)
            else:
                model_instance.create(data)

            return redirect(reverse('ims:model_list', kwargs={'model_name': model_name}))
        
        # Add supplier and category context for products
        if model_name == 'product':
            categories = Category().all()
            suppliers = Supplier().all()
            context = {
                'item': None,
                'categories': categories,
                'suppliers': suppliers
            }
            return render(request, f'ims/{model_name}/{model_name}_form.html', context)

        return render(request, f'ims/{model_name}/{model_name}_form.html', {'item': None})

    except Http404:
        return render(request, 'ims/404.html')

@login_required
def model_update(request, model_name, item_id):
    try:
        model_class = get_model_instance(model_name)
        model_instance = model_class()  
        item = model_instance.read(item_id)  

        if not item:
            raise Http404(f"{model_name.capitalize()} with ID {item_id} does not exist.")

        if request.method == 'POST':
            data = request.POST.dict()
            data.pop('csrfmiddlewaretoken', None)

            image_file = request.FILES.get('image')

            if model_name == 'product':
                if image_file:
                    if 'image_url' in item:
                        model_instance.delete_image(item['image_url'])
                    model_instance.update(item_id, data, image_file=image_file)  
                else:
                    model_instance.update(item_id, data)

            else:
                model_instance.update(item_id, data)        

            return redirect(reverse('ims:model_list', args=[model_name]))
        
        # Prepare context for rendering the form
        context = {'item': item}

        if model_name == 'product':
            categories = Category().all()
            suppliers = Supplier().all()
            context['categories'] = categories
            context['suppliers'] = suppliers

        return render(request, f'ims/{model_name}/{model_name}_form.html', context)

    except Http404:
        return render(request, 'ims/404.html')


@login_required
def model_delete(request, model_name, item_id):
    try:
        model_class = get_model_instance(model_name)
        model_instance = model_class()
        item = model_instance.read(item_id)

        if not item:
            raise Http404(f"{model_name.capitalize()} with ID {item_id} does not exist.")

        model_instance.delete(item_id)  
        return redirect(reverse('ims:model_list', args=[model_name]))

    except Http404:
        return render(request, 'ims/404.html')