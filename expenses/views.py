from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Category, Expense
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from dateutil.relativedelta import relativedelta
import matplotlib.pyplot as plt
import io
import base64
import datetime
import json
import calendar

# Ensure that the user is logged in before accessing this view, redirect to the login page if not
@login_required(login_url='/accounts/login')
def index(request):
    expenses = Expense.objects.filter(owner=request.user)
    paginator = Paginator(expenses, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)


    context = {
        'expenses': expenses,
        'page_obj': page_obj,
    }
    return render(request, 'expenses/index.html', context)

# Ensure that the user is logged in before accessing this view, redirect to the login page if not
@login_required(login_url='/accounts/login')
def monthly_report(request):
    if request.method == 'GET':
        # Get the selected month from the request
        selected_month = request.GET.get('selected_month', None)
        
        # Validate the selected_month (e.g., check for valid input)
        if selected_month is not None:
            try:
                selected_month = int(selected_month)
                if 1 <= selected_month <= 12:
                    # Get the current year
                    today = datetime.date.today()
                    year = today.year

                    # Calculate the first and last days of the selected month
                    first_day = datetime.date(year, selected_month, 1)
                    # Calculate the last day of the current month
                    last_day = calendar.monthrange(year, selected_month)[1]

                    # Fetch expenses for the selected month
                    expenses = Expense.objects.filter(
                        owner=request.user,
                        date__range=[datetime.datetime(year, selected_month, 1), datetime.datetime(year, selected_month, last_day)]
                    )

                    finalrep = {}

                    def get_category(expense):
                        return expense.category

                    category_list = list(set(map(get_category, expenses)))

                    for category in category_list:
                        filtered_by_category = expenses.filter(category=category)
                        total_amount = sum(item.amount for item in filtered_by_category)
                        finalrep[category] = total_amount

                    # Create data for visualization
                    categories = []
                    amounts = []
                    
                    for key, value in finalrep.items():
                        categories.append(key)
                        amounts.append(value)

                    # Create a pie chart
                    plt.figure(figsize=(8, 8))
                    plt.pie(amounts, labels=categories, autopct='%1.1f%%')
                    plt.title(f'Spending by Category for {first_day.strftime("%B %Y")}')

                    # Save the chart to a file-like object
                    buffer = io.BytesIO()
                    plt.savefig(buffer, format='png')
                    buffer.seek(0)
                    plt.close()

                    # Encode the chart to base64
                    chart = base64.b64encode(buffer.read()).decode()
                    months = [{'value': month, 'label': datetime.date(1, month, 1).strftime("%B")} for month in range(1, 13)]
                    context = {
                        'chart': chart,
                        'selected_month': selected_month,
                        'months':months
                    }

                    return render(request, 'expenses/monthly_report.html', context)
                else:
                    return HttpResponse("Invalid month selected")
            except ValueError:
                return HttpResponse("Invalid month selected")
    
    # Default view when no month is selected
    months = [{'value': month, 'label': datetime.date(1, month, 1).strftime("%B")} for month in range(1, 13)]

    context = {
        'months': months
    }

    return render(request, 'expenses/monthly_report.html', context)
    
# Ensure that the user is logged in before accessing this view, redirect to the login page if not
@login_required(login_url='/accounts/login')
def monthwise_report(request):
    # Get the current year
    today = datetime.date.today()
    year = today.year

    # Fetch all expenses for the current year
    start_date = datetime.date(year, 1, 1)
    end_date = datetime.date(year, 12, 31)

    expenses = Expense.objects.filter(
        owner=request.user,
        date__range=[start_date, end_date]
    )

    # Create a dictionary to store month-wise total expenses
    month_expenses = {}

    for month in range(1, 13):
        # Calculate first and last day of the current month
        first_day = datetime.date(year, month, 1)
        # Calculate the last day of the current month
        last_day = calendar.monthrange(year, month)[1]

        # Fetch expenses for the current month
        monthly_expenses = expenses.filter(
            date__range=[datetime.datetime(year, month, 1), datetime.datetime(year, month, last_day)]
        )


        # Calculate the total expense for the current month
        total_expense = sum(expense.amount for expense in monthly_expenses)
        
        # Store the total expense in the dictionary
        month_expenses[month] = total_expense


    # Convert month numbers to strings
    months = [datetime.date(year, month, 1).strftime("%B") for month in range(1, 13)]

    # Retrieve the total expenses for each month
    total_expenses = [month_expenses.get(month, 0) for month in range(1, 13)]


    # Create a bar graph
    plt.figure(figsize=(12, 6)) 
    plt.bar(months, total_expenses)
    plt.xlabel('Month')
    plt.ylabel('Total Expenses')
    plt.title('Total Expenses by Month')

    # Save the graph to a file-like object
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close()

    # Encode the graph to base64
    graph = base64.b64encode(buffer.read()).decode()

    context = {
        'graph': graph,
        'months_expenses': month_expenses
    }

    return render(request, 'expenses/monthwise_report.html', context)
    
# Ensure that the user is logged in before accessing this view, redirect to the login page if not
@login_required(login_url='/accounts/login')
def daywise_expenses(request):
    # Get the selected month from the request
    if request.method == 'GET':
        # Get the selected month from the request
        selected_month_str = request.GET.get('selected_month', None)


        # Validate the selected_month (e.g., check for valid input)
        if selected_month_str is not None:
            # Calculate the first and last day of the selected month
            try:
                selected_month = int(selected_month_str)
                if 1 <= selected_month <= 12:
                    # Get the current year
                    today = datetime.date.today()
                    year = today.year
                    first_day = datetime.datetime(year, selected_month, 1)  # Convert to datetime
                    last_day = datetime.datetime(year, selected_month, calendar.monthrange(year, selected_month)[1])  # Convert to datetime

                    # Now you can use these datetime objects in the date__range query
                    expenses = Expense.objects.filter(
                        owner=request.user,
                        date__range=[first_day, last_day]
                    )

                    # Create a dictionary to store day-wise total expenses
                    daywise_expenses = {}

                    for day in range(1, last_day.day + 1):
                        current_date = datetime.date(year, selected_month, day)

                        # Calculate the total expense for the current day
                        day_expenses = expenses.filter(date=current_date)

                        total_expense = sum(expense.amount for expense in day_expenses)

                        # Store the total expense in the dictionary
                        daywise_expenses[day] = total_expense

                    # Create a bar graph
                    plt.figure(figsize=(12, 6))
                    plt.bar(daywise_expenses.keys(), daywise_expenses.values())
                    plt.xlabel('Day')
                    plt.ylabel('Total Expenses')
                    plt.title(f'Total Expenses for {first_day.strftime("%B")} {year}')

                    # Save the graph to a file-like object
                    buffer = io.BytesIO()
                    plt.savefig(buffer, format='png')
                    buffer.seek(0)
                    plt.close()

                    # Encode the graph to base64
                    graph = base64.b64encode(buffer.read()).decode()
                    # Default view when no month is selected
                    months = [{'value': month, 'label': datetime.date(1, month, 1).strftime("%B")} for month in range(1, 13)]
                    context = {
                        'graph': graph,
                        'day_expenses': daywise_expenses,
                        'selected_month': selected_month,
                        'months': months
                    }

                    return render(request, 'expenses/daywise_expenses.html', context)
                else:
                    return HttpResponse("Invalid month selected")
            except ValueError:
                return HttpResponse("Invalid month selected")
    
    # Default view when no month is selected
    months = [{'value': month, 'label': datetime.date(1, month, 1).strftime("%B")} for month in range(1, 13)]
    context = {
        'months': months
    }
    return render(request, 'expenses/daywise_expenses.html', context)


# Ensure that the user is logged in before accessing this view, redirect to the login page if not
@login_required(login_url='/accounts/login')
def add_expense(request):
    # Retrieve all categories from the database
    categories = Category.objects.all()

    # Prepare the context data to be passed to the template
    context = {
        'categories': categories,
        'values': request.POST
    }

    # If the request method is GET, render the template for adding an expense with the provided context
    if request.method == 'GET':
        return render(request, 'expenses/add_expense.html', context)

    # If the request method is POST, process the form data
    if request.method == 'POST':
        # Retrieve the amount from the form data
        amount = request.POST['amount']

        # Check if the amount is not provided, display an error message
        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'expenses/add_expense.html', context)

        # Retrieve other form data: description, date, and category
        description = request.POST['description']
        date = request.POST['date']
        category = request.POST['category']

        # Check if description is not provided, display an error message
        if not description:
            messages.error(request, 'Description is required')
            return render(request, 'expenses/add_expense.html', context)

        # Check if date is not provided, display an error message
        if not date:
            messages.error(request, 'Date is required')
            return render(request, 'expenses/add_expense.html', context)

        # Create a new Expense object in the database with the provided data
        Expense.objects.create(owner=request.user, amount=amount, date=date,
                               category=category, description=description)
        
        # Display a success message
        messages.success(request, 'Expense saved successfully')

        # Redirect to the 'expenses' page after successfully adding an expense
        return redirect('expenses')



# Ensure that the user is logged in before accessing this view, redirect to the login page if not
@login_required(login_url='/accounts/login')
def expense_edit(request, id):
    # Retrieve the Expense object from the database using the provided id
    expense = Expense.objects.get(pk=id)

    # Retrieve all categories from the database
    categories = Category.objects.all()

    # Prepare the context data to be passed to the template
    context = {
        'expense': expense,
        'values': expense, 
        'categories': categories
    }

    # If the request method is GET, render the template for editing an expense with the provided context
    if request.method == 'GET':
        return render(request, 'expenses/edit_expense.html', context)

    # If the request method is POST, process the form data
    if request.method == 'POST':
        # Retrieve the amount from the form data
        amount = request.POST['amount']

        # Check if the amount is not provided, display an error message
        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'expenses/edit_expense.html', context)

        # Retrieve other form data: description, date, and category
        description = request.POST['description']
        date = request.POST['expense_date']
        category = request.POST['category']

        # Check if description is not provided, display an error message
        if not description:
            messages.error(request, 'Description is required')
            return render(request, 'expenses/edit_expense.html', context)

        # Update the Expense object with the new data
        expense.owner = request.user
        expense.amount = amount
        expense.date = date
        expense.category = category
        expense.description = description

        # Save the updated expense object in the database
        expense.save()

        # Display a success message
        messages.success(request, 'Expense updated successfully')

        # Redirect to the 'expenses' page after successfully updating an expense
        return redirect('expenses')


# Ensure that the user is logged in before accessing this view, redirect to the login page if not
@login_required(login_url='/accounts/login')
def delete_expense(request, id):
    # Retrieve the Expense object from the database using the provided id
    expense = Expense.objects.get(pk=id)

    # Delete the expense from the database
    expense.delete()

    # Display a success message
    messages.success(request, 'Expense removed')

    # Redirect to the 'expenses' page after successfully deleting an expense
    return redirect('expenses')


# Ensure that the user is logged in before accessing this view, redirect to the login page if not
@login_required(login_url='/accounts/login')
def expense_category_summary(request, period):
    # Get the current date
    todays_date = datetime.date.today()

    # Determine the start and end dates based on the specified period
    if period == 'day':
        start_date = todays_date
        end_date = todays_date
    elif period == 'month':
        start_date = todays_date.replace(day=1)
        end_date = todays_date
    elif period == 'year':
        start_date = todays_date.replace(month=1, day=1)
        end_date = todays_date.replace(month=12, day=31)
    else:
        # Handle an invalid period gracefully, you can redirect or show an error message.
        return HttpResponseBadRequest("Invalid period")

    # Retrieve expenses from the database within the specified date range
    expenses = Expense.objects.filter(
        owner=request.user,
        date__gte=start_date,
        date__lte=end_date
    )

    # Initialize variables for the final report and total expenses
    finalrep = {}
    total_expenses = 0

    # Helper function to extract the category from an expense
    def get_category(expense):
        return expense.category

    # Create a list of unique categories from the expenses
    category_list = list(set(map(get_category, expenses)))

    # Calculate total expenses for each category
    for category in category_list:
        # Filter expenses by category
        filtered_by_category = expenses.filter(category=category)

        # Calculate the total amount for the category
        total_amount = sum(item.amount for item in filtered_by_category)

        # Update the final report with the total amount for the category
        finalrep[category] = total_amount

        # Update the total expenses
        total_expenses += total_amount

    # Prepare the context data to be passed to the template
    context = {
        'expense_category_data': finalrep,
        'total_expenses': total_expenses,
        'period': period,
    }

    # Render the template for displaying the expense category summary with the provided context
    return render(request, 'expenses/expense_category_summary.html', context)

# Ensure that the user is logged in before accessing this view, redirect to the login page if not
@login_required(login_url='/accounts/login')
def settings(request):
    return render(request, 'settings.html')
    
