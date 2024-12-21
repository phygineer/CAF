// docker.service.ts
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

interface Container {
  id: string;
  name: string;
  status: string;
  image: string[];
}

@Injectable({
  providedIn: 'root'
})
export class DockerService {
  private baseUrl = 'http://localhost:8000/api';  // FastAPI base URL

  constructor(private http: HttpClient) {}

  dockerCheck(): Observable<{ status: string }> {
    return this.http.get<{ status: string }>(`${this.baseUrl}/docker-check`);
  }

  listContainers(allContainers: boolean = false): Observable<Container[]> {
    return this.http.get<Container[]>(`${this.baseUrl}/containers?all_containers=${allContainers}`);
  }

  createContainer(name?: string): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/containers`, { name });
  }

  getContainerDetails(containerId: string): Observable<Container> {
    return this.http.get<Container>(`${this.baseUrl}/containers/${containerId}`);
  }

  stopContainer(containerId: string): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/containers/${containerId}/stop`, {});
  }

  removeContainer(containerId: string): Observable<any> {
    return this.http.delete<any>(`${this.baseUrl}/containers/${containerId}`);
  }
}
