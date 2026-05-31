from django import forms

from engine.models import Genre

class BookFilterForm(forms.Form):
    query = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'filter-input',
            'placeholder': 'Введите название книги',
        })
    )
    genre = forms.ModelChoiceField(
        queryset=Genre.objects.all(),
        empty_label="Все жанры",
        label="Выберите жанр",
        widget=forms.Select(attrs={'class': 'filter-input'}),
        required=False
    )
    year = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'filter-input',
            'placeholder': 'Год',
        })
    )
    author = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'filter-input',
            'placeholder': 'Автор',
        })
    )
