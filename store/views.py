from django.contrib.auth.models import AnonymousUser
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from store.models import *
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from django.http import JsonResponse, Http404
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

# Create your views here.

def index(request):
    return render(request, 'store/index.html')

def bookDetailView(request, bid):
    template_name = 'store/book_detail.html'
    book = get_object_or_404(Book, id=bid)
    num_available = BookCopy.objects.filter(book=book, status=True).count()
    if request.user.is_anonymous:
        current_user_rated = None
    else:
        try:
            current_user_rated = BookRating.objects.get(book=book, user=request.user)
        except ObjectDoesNotExist:
            current_user_rated = None
    context = {
        'book': book, # set this to an instance of the required book
        'num_available': num_available, # set this to the number of copies of the book available, or 0 if the book isn't available
        'current_user_rated': current_user_rated,
    }
    # START YOUR CODE HERE
    
    
    return render(request, template_name, context=context)


@csrf_exempt
def bookListView(request):
    template_name = 'store/book_list.html'
    get_data = request.GET
    books = Book.objects.filter(
        title__icontains = get_data.get('title',''),
        author__icontains = get_data.get('author',''),
        genre__icontains = get_data.get('genre',''),
    )
    context = {
        'books': books, # set this to the list of required books upon filtering using the GET parameters
    }
    # START YOUR CODE HERE
    
    
    return render(request, template_name, context=context)

@login_required
def viewLoanedBooks(request):
    template_name = 'store/loaned_books.html'
    books = BookCopy.objects.filter(borrower=request.user)
    context = {
        'books': books,
    }
    '''
    The above key 'books' in the context dictionary should contain a list of instances of the 
    BookCopy model. Only those book copies should be included which have been loaned by the user.
    '''
    # START YOUR CODE HERE
    


    return render(request, template_name, context=context)

@csrf_exempt
@login_required
def loanBookView(request):
    response_data = {
        'message': None,
    }
    '''
    Check if an instance of the asked book is available.
    If yes, then set the message to 'success', otherwise 'failure'
    '''
    # START YOUR CODE HERE
    book_id = request.POST['bid'] # get the book id from post data

    try:
        book = Book.objects.get(id=book_id)
    except:
        raise Http404('Book not available')
    else:
        books = BookCopy.objects.filter(book=book, status=True)

        if books:
            books[0].borrow_date = timezone.datetime.today().date()
            books[0].status = False
            books[0].borrower = request.user
            books[0].save()
            response_data['message'] = 'success'
        else:
            response_data['message'] = 'failure'


    return JsonResponse(response_data)

'''
FILL IN THE BELOW VIEW BY YOURSELF.
This view will return the issued book.
You need to accept the book id as argument from a post request.
You additionally need to complete the returnBook function in the loaned_books.html file
to make this feature complete
''' 
@csrf_exempt
@login_required
def returnBookView(request):
    response_data = {
        'message': None,
    }

    book_copy_id = request.POST['bid']

    book = get_object_or_404(BookCopy, id=book_copy_id)

    if book and book.borrower == request.user:
        book.borrower = None
        book.borrow_date = None
        book.status = True
        book.save()
        response_data['message'] = 'success'
    else:
        response_data['message'] = 'failure'
    return JsonResponse(response_data)

@csrf_exempt
@login_required
def rateBookView(request):
    if request.method == "POST":
        bid = request.POST['bid']
        new_rating = request.POST['rating']
        if int(new_rating) >= int(0) and int(new_rating) <= int(10):
            try:
                book = Book.objects.get(pk=bid)
                user = User.objects.get(username = request.user.username)
                try:
                    previous_user_rating = BookRating.objects.get(book=book, user=user)
                except ObjectDoesNotExist:
                    previous_user_rating = BookRating()
                if previous_user_rating.rating is None:
                    previous_user_rating.book = book
                    previous_user_rating.user = user
                previous_user_rating.rating = new_rating
                previous_user_rating.save()
                book.rating = BookRating.objects.filter(book=book).aggregate(rating=Avg('rating'))['rating']
                book.rating = round(book.rating, 2)
                book.save()
            except:
                return JsonResponse({'message': 'error'})
            else:
                return JsonResponse({'message': 'success'})
        else:
            return JsonResponse({'message': 'Rating must be from 0 to 10'})
    else:
        return JsonResponse({'message': "invalid request method"})
