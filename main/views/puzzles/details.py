# francontcube/views/puzzle/detail.py

from django.shortcuts import get_object_or_404, render
from cube.models import PuzzleCase

def puzzle_case_detail(request, slug):
    case = get_object_or_404(PuzzleCase, slug=slug)
    return render(request, 'puzzle/detail.html', {'case': case})