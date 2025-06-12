from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import JsonResponse
from .models import Book
from .serializers import BookSerializer
from .decorators import require_api_key
import imghdr

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    def get_queryset(self):
        return Book.objects.all()

    def create(self, request, *args, **kwargs):
        return require_api_key(super().create)(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return require_api_key(super().update)(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        return require_api_key(super().destroy)(request, *args, **kwargs)

    @action(detail=True, methods=['post'], url_path='upload-cover')
    @require_api_key
    def upload_cover(self, request, pk=None):
        try:
            book = self.get_object()
            file = request.FILES.get('cover')

            if not file:
                return JsonResponse({'error': 'NO_FILE', 'message': 'No file uploaded'}, status=400)

            if file.size > 2 * 1024 * 1024:
                return JsonResponse({'error': 'FILE_TOO_LARGE', 'message': 'Max size is 2MB'}, status=413)

            file_type = imghdr.what(file)
            if file_type not in ['jpeg', 'png', 'webp']:
                return JsonResponse({
                    'error': 'INVALID_FILE_TYPE',
                    'message': 'Only JPG, PNG, and WEBP files are allowed',
                    'allowed_types': ['jpg', 'png', 'webp'],
                    'received_type': file_type
                }, status=400)

            book.cover_image = file
            book.save()

            return JsonResponse({
                'id': book.id,
                'title': book.title,
                'cover_url': request.build_absolute_uri(book.cover_image.url),
                'message': 'Cover uploaded successfully'
            }, status=200)

        except Book.DoesNotExist:
            return JsonResponse({'error': 'NOT_FOUND', 'message': 'Book not found'}, status=404)
