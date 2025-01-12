from django.shortcuts import render,redirect,get_object_or_404
from.models import *
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib import messages
from datetime import datetime,date
from django.db.models import Sum
from django.db.models.functions import ExtractMonth, ExtractYear
from datetime import date
from django.db.models import Q



# Create your views here.

def index(request):
    
    
    return render(request, 'index.html')



def login(request):
    if request.method == "POST":
        email = request.POST.get("username")  
        password = request.POST.get("Password")

        # Authenticate user
        user = authenticate(username=email, password=password)
        if user is not None:
            # Flush previous session and set new session data
            request.session.flush()
            request.session['email'] = email

            # Check user roles and redirect accordingly
            if user.is_superuser:
                return redirect("/adminhome")
            elif user.is_staff:
                try:
                    expert = Expert.objects.get(email=email)
                    request.session['id'] = expert.id
                    return redirect("/experthome")
                except Expert.DoesNotExist:
                    messages.error(request, "No expert details found.")
                    return render(request, "login.html")
            else:
                try:
                    sf = Users.objects.get(email=email)
                    request.session['id'] = sf.id
                    return redirect("/userhome")
                except Users.DoesNotExist:
                    messages.error(request, "No user details found.")
                    return render(request, "login.html")
        else:
            # Handle invalid credentials or inactive account
            try:
                user = User.objects.get(username=email)
                if not user.is_active:
                    messages.error(request, "Your account is not active. Please contact support.")
                else:
                    messages.error(request, "Invalid password. Please try again.")
            except User.DoesNotExist:
                messages.error(request, "No account found with this email.")
            return render(request, "login.html")

    return render(request, "login.html")

def user_reg(request):
    today=date.today()
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        password = request.POST.get("password")
        income = request.POST.get("income")
        amount=request.POST.get("budget")

        
        if User.objects.filter(username=email).exists():
            messages.error(request, "Email already exists.")
        else:
            if int(income) < int(amount):
                messages.error(request, "Budget cannot be higher than income.")
            else:
                user = User.objects.create_user(
                    username=email, password=password, is_staff=0, is_active=1)
                user.save()

                inv = Users.objects.create(name=name, email=email, phone=phone, income=income, user=user)
                inv.save()

                Budget.objects.create(user=inv, amount=amount, date=today)

                messages.success(request, "Registration Successful.")
                return render(request, 'user_reg.html')

    return render(request, 'user_reg.html')

def exp_reg(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        exp = request.POST.get("exp")
        password = request.POST.get("password")

        if User.objects.filter(username=email).exists():
            messages.error(request, "Email already exists.")
        else:
            user = User.objects.create_user(
                username=email, password=password, is_staff=0, is_active=1)
            user.save()

            inv = Expert.objects.create(name=name, email=email, exp=exp, user=user)
            inv.save()

            messages.success(request, "Registration Successful.")
            return render(request, 'exp_reg.html')

    return render(request, 'exp_reg.html')

def adminhome(request):

    return render(request, 'adminhome.html')

def userhome(request):
    total_expense = 0
    user = Users.objects.get(id=request.session['id'])
    income=int(user.income)
    expenses = Expense.objects.filter(user=user)
    budget=Budget.objects.filter(user=user)
    for expense in expenses:
        total_expense += expense.amount
#data for monthly chart
    year = request.GET.get('year', date.today().year)  # Default to current year

    # Get expenses for the selected year grouped by month
    expenses_by_month = (
        Expense.objects.filter(user=user, date__year=year)
        .annotate(month=ExtractMonth('date'))
        .values('month')
        .annotate(total_expense=Sum('amount'))
        .order_by('month')
    )

    # Prepare data for the chart
    labels = []
    data = []

    for entry in expenses_by_month:
        labels.append(f"{year}-{entry['month']:02d}")  # e.g., "2024-12"
        data.append(entry['total_expense'])

    # Get all distinct years with expenses for the dropdown
    years = Expense.objects.filter(user=user).annotate(year=ExtractYear('date')).values_list('year', flat=True).distinct()


    context={
        'expense':total_expense,
        'income':income,
        'savings':income-total_expense,
        'budget':budget[0].amount,
        'user':user,
        'labels': labels,
        'data': data,
        'selected_year': int(year),
        'years': sorted(years),
        }
    

    return render(request, 'userhome.html',context)

def experthome(request):
    
    return render(request, 'exphome.html')



def add_expense(request):
    total_expense = 0
    user = Users.objects.get(id=request.session['id'])
    income = user.income

    # Calculate total expenses
    expenses = Expense.objects.filter(user=user)
    for expense in expenses:
        total_expense += expense.amount

    # Get the budget for the current month
    today = date.today()
    budget = Budget.objects.filter(
        user=user,
        date__month=today.month,
        date__year=today.year
    ).first()

    # Handle no budget case
    if not budget:
        messages.error(request, "No budget set for the current month.")
        return redirect('/add_expense')

    # Calculate balance
    balance = budget.amount - total_expense

    if request.method == "POST":
        amount = request.POST.get("amount")
        category = request.POST.get("category")

        try:
            amount = float(amount)
            if total_expense + amount <= income:
                # Add the expense
                Expense.objects.create(user=user, amount=amount, date=today, category=category)
                messages.success(request, "Expense added successfully!")
                return redirect('/add_expense')
            else:
                messages.error(request, "Total expense cannot exceed your income.")
        except ValueError:
            messages.error(request, "Invalid amount. Please enter a valid number.")

    # Render the template with necessary context
    context = {
        'expenses': expenses,
        'balance': balance,
        'budget': budget.amount,  # Extracting the actual budget value
    }
    return render(request, 'add_expense.html', context)


def remove_expense(request):
    id=request.GET.get('id')
    expense = Expense.objects.get(id=id)
    expense.delete()
    
    return redirect('/add_expense')

def edit_expense(request):
    id=request.GET.get('id')
    expense = Expense.objects.get(id=id)
    if request.method == "POST":
        amount = request.POST.get("amount")
        date = datetime.now()
        category = request.POST.get("category")
        expense.amount = amount
        expense.date = date
        expense.category = category
        expense.save()
        return redirect('/add_expense')
    return render(request, 'edit_expense.html', {'expense': expense})

# user can set budget only once in a month and send budget to template and store in the budget table
def set_budget(request):
    total_goal = 0
    total_expense = 0
    today = date.today()
    current_month = today.month
    current_year = today.year
    user=Users.objects.get(id=request.session['id'])
    income=user.income
    expense=Expense.objects.filter(user=user)
    for i in expense:
        total_expense += i.amount
        
    # Check if a budget for the current month already exists
    current_budget = Budget.objects.filter(
        user=user,
        date__month=current_month,
        date__year=current_year
    ).first()

    if request.method == "POST":
        amount = request.POST.get("budget")
        if int(amount) < income:
            if current_budget:
             # Update the existing budget
                current_budget.amount = amount
                current_budget.save()
                messages.success(request, "Budget updated successfully!")
            else:
            # Create a new budget for the current month
                Budget.objects.create(
                    user=user,
                    amount=amount,
                    date=today
                )
                messages.success(request, "Budget set successfully!")
                
            return redirect("set_budget")
        else:
            messages.error(request, "Budget cannot be higher than income.")
            return redirect("set_budget")
        
        # Get existing goals
    goals = Goal.objects.filter(user=user)

    #total amount of goals
    for goal in goals:
        total_goal += goal.set_amount

        

    return render(request, "set_budget.html", {
        "expense": total_expense,'balance':current_budget.amount-total_expense-total_goal,'budget':current_budget.amount})
# set savings goal for the user and store in the goal table also update amount for goal the goal cannot be more than the balance after the budget is set

def set_saving_goal(request):
    total_goal = 0
    total_expense = 0
    today = date.today()
    current_month = today.month
    current_year = today.year

    user = Users.objects.get(id=request.session['id'])
    income = user.income

    expenses = Expense.objects.filter(user=user)
    for expense in expenses:
        total_expense += expense.amount

    budget = Budget.objects.filter(
        user=user,
        date__month=current_month,
        date__year=current_year
    ).first()

    if not budget:
        messages.error(request, "No budget set for the current month.")
        return redirect("set_budget")

    balance = budget.amount - total_expense

    if request.method == "POST":
        goal = request.POST.get("goal")
        amount = request.POST.get("amount")
        Goal.objects.create(
            user=user,
            goal=goal,
            amount=amount,
            set_amount=0,
            date=today
            )
        messages.success(request, "Goal set successfully!")
        return redirect("set_saving_goal")


    # Get existing goals
    goals = Goal.objects.filter(user=user)

    #total amount of goals
    for goal in goals:
        total_goal += goal.set_amount
    
    # Render the template with context
    context = {
        'goals': goals,
        'expense': total_expense,
        'balance': balance-total_goal,
        'total_goal': total_goal
    }
    return render(request, "user_saving_goal.html", context)
#monthly update goal if the added amount is less than balance after budget is set and update the amount in the goal table and also give a notification when goal and achieved 
 
def update_goal(request):
    today = date.today()
    current_month = today.month
    current_year = today.year

    # Get the user
    user = Users.objects.get(id=request.session['id'])
    income = user.income

    # Calculate total expenses
    expenses = Expense.objects.filter(user=user)
    total_expense = 0
    for expense in expenses:
        total_expense += expense.amount

    # Get the budget for the current month
    budget = Budget.objects.filter(
        user=user,
        date__month=current_month,
        date__year=current_year
    ).first()

    # Handle missing budget
    if not budget:
        messages.error(request, "No budget set for the current month.")
        return redirect("set_budget")

    balance = budget.amount - total_expense

    if request.method == "POST":
        goal_id = request.POST.get("id")
        amount = request.POST.get("g_amount")
        goal = Goal.objects.get(id=goal_id)
        if int(amount) <= balance:
            goal.set_amount += int(amount)
            goal.save()
            messages.success(request, "Goal updated successfully!")
        else:
            messages.error(request, "Amount cannot be higher than balance.")
        return redirect("set_saving_goal")

    return redirect("set_saving_goal")

def user_update_profile(request):
    user = Users.objects.get(id=request.session['id'])
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        income = request.POST.get("income")
        user.name = name
        user.email = email
        user.phone = phone
        user.income = income
        user.save()
        messages.success(request, "Profile updated successfully!")
        return redirect("user_update_profile")
    return render(request, "user_update_profile.html", {'user': user})

#admin can approve the user to login and admin can view each user details 

def admin_user_approve(request):
    users = Users.objects.all()  # Fetch all users

    if request.method == "POST":
        action = request.POST.get("action")  # Get action: approve or block
        user_id = request.POST.get("id")  # Get user ID
        try:
            user = Users.objects.get(id=user_id)  # Fetch the user
            if action == "approve":
                user.user.is_active = True
                user.user.save()
                
            elif action == "block":
                user.user.is_active = False
                user.user.save()
               
        except Users.DoesNotExist:
            messages.error(request, "User not found!")
        return redirect("admin_user_approve")

    return render(request, 'admin_user_approve.html', {'users': users})
#when admin click on view button he can see the details of the user

def view_user_details(request, user_id):
    # Get user details
    user = get_object_or_404(Users, id=user_id)
    
    # Calculate total income, expense, and budget
    total_income = user.income
    total_expenses = Expense.objects.filter(user=user).aggregate(Sum('amount'))['amount__sum'] or 0
    budget = total_income - total_expenses

    # Get unique years of expenses for the dropdown
    expense_years = Expense.objects.filter(user=user).dates('date', 'year')
    years = [year.year for year in expense_years]

    # Get the selected year from the dropdown, or default to the current year
    selected_year = request.GET.get('year', date.today().year)
    
    # Filter expenses for the selected year
    monthly_expenses = (
        Expense.objects.filter(user=user, date__year=selected_year)
        .values('date__month')
        .annotate(total=Sum('amount'))
        .order_by('date__month')
    )

    # Prepare data for the chart
    chart_data = [0] * 12  # Initialize with 12 months
    for expense in monthly_expenses:
        chart_data[expense['date__month'] - 1] = expense['total']

    # Pass context to the template
    context = {
        'user': user,
        'income': total_income,
        'expense': total_expenses,
        'budget': budget,
        'years': years,
        'selected_year': int(selected_year),
        'chart_data': chart_data,
    }
    return render(request, 'view_user_details.html', context)

#admin want to approve the expert to login and view the expert details
def admin_expert_approve(request):
    experts = Expert.objects.all()  # Fetch all experts

    if request.method == "POST":
        action = request.POST.get("action")  # Get action: approve or block
        expert_id = request.POST.get("id")  # Get expert ID
        try:
            expert = Expert.objects.get(id=expert_id)  # Fetch the expert
            if action == "approve":
                expert.user.is_active = True
                expert.user.save()
            elif action == "block":
                expert.user.is_active = False
                expert.user.save()
        except Expert.DoesNotExist:
            messages.error(request, "Expert not found!")
        return redirect("admin_expert_approve")

    return render(request, 'admin_expert_approve.html', {'experts': experts})

def expert_user_view(request):
    users = Users.objects.all()
    return render(request, 'expert_user_view.html', {'users': users})



def expert_chat(request):
    # Ensure the expert is logged in by checking if the session has 'id'
    if 'id' not in request.session:
        messages.error(request, "You need to log in first.")
        return redirect('expert_login')  # Redirect to the login page if the session is invalid
    expert_id = request.session['id']
    try:
        # Fetch the expert from the session ID
        expert = Expert.objects.get(id=expert_id)

        # Get the user from the query parameter (uid)
        uid = request.GET.get('uid')
        
        if uid is None:
            messages.error(request, "No user specified.")
            return redirect('experthome')  # Redirect if no user ID is provided
        
        # Fetch the user by their ID
        user = Users.objects.get(id=uid)
        
        # Initialize the sender (expert) and receiver (user) email
        sender = expert.email
        receiver = user.email

        # Handle POST request to send messages
        if request.method == "POST":
            message = request.POST.get('msg')
            if message:
                Chat.objects.create(sender=sender, receiver=receiver, message=message)
                return redirect(f'/expert_chat/?uid={uid}')  # Redirect to refresh chat

        # Retrieve all messages between the expert and the user, ordered by date
        messages = Chat.objects.filter(sender=sender, receiver=receiver) | Chat.objects.filter(sender=receiver, receiver=sender)
        messages = messages.order_by('date')

        return render(request, 'expert_chat.html', {
            'messages': messages,
            'sender': sender,
            'receiver': receiver,
            'expert': expert,  # Add expert to the context (optional)
        })

    except Expert.DoesNotExist:
        messages.error(request, "Expert not found!")
        return redirect('expert_login')  # Redirect to login if expert doesn't exist

    except Users.DoesNotExist:
        messages.error(request, "User not found!")
        return redirect('experthome')  # Redirect if user doesn't exist
    
def view_experts(request):
    experts = Expert.objects.all()
    return render(request, 'view_experts.html', {'experts': experts})



def user_chat(request):
    # Get the logged-in user's ID from the session
    uid = request.session.get('id')
    if not uid:
        return redirect('user_login')  # Redirect to login if session is missing
    
    # Fetch user and expert details
    user = Users.objects.get(id=uid)
    sender = user.email
    exp_id = request.GET.get('uid')
    try:
        expert = Expert.objects.get(id=exp_id)
    except Expert.DoesNotExist:
        return redirect('view_experts')  # Redirect if the expert doesn't exist
    
    receiver = expert.email
    if request.method == "POST":
        # Handle message submission
        message = request.POST.get('msg')
        Chat.objects.create(sender=sender, receiver=receiver, date=datetime.now(), message=message)
        return redirect(f'/user_chat?uid={exp_id}')  # Redirect to the same chat view
    
    # Fetch chat messages between the user and the expert
    messages = Chat.objects.filter(
        (Q(sender=sender) & Q(receiver=receiver)) |
        (Q(sender=receiver) & Q(receiver=sender))
    ).order_by('date')
    
    return render(request, 'user_chat.html', {
        'messages': messages,
        'sender': sender,
        'receiver': receiver,
        'expert': expert,
        'exp_id': exp_id,
    })



