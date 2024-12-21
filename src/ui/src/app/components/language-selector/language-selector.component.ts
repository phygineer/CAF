import { Component } from '@angular/core';
import { DataService } from '../../services/data.service';
import { NgFor } from '@angular/common';

@Component({
  selector: 'app-language-selector',
  imports: [NgFor],
  templateUrl: './language-selector.component.html',
  styleUrl: './language-selector.component.scss'
})
export class LanguageSelectorComponent {
  languages=[];

  constructor(private dataService: DataService) {}

  ngOnInit() {
    this.dataService.getLanguagesData().subscribe({
      next: (data) => {
        this.languages = data;
        console.log('Data received:', data);
      },
      error: (error) => {
        console.error('Error fetching data:', error);
      },
    });
  }
}
