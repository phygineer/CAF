import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class DataService {
  constructor(private http: HttpClient) {}

  getLanguagesData(): Observable<any> {
    // Specify the path to your JSON file in the assets folder
    return this.http.get<any>('./assets/languages.json');
  }
}
