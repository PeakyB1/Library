from django import forms

class BookFilterForm(forms.Form):
    query = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'filter-input',
            'placeholder': 'Введите название книги',
        })
    )
    genre = forms.ChoiceField(
        choices=[], 
        required=False,
        widget=forms.Select(attrs={
            'class': 'filter-select',
        })
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

    def __init__(self, *args, **kwargs):
        genres = kwargs.pop('genres', [])
        super().__init__(*args, **kwargs)
        self.fields['genre'].choices = [('', 'Все жанры')] + [(genre.id, genre.name) for genre in genres]