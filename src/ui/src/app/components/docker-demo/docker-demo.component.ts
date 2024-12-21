// docker-demo.component.ts
import { Component, OnInit } from '@angular/core';
import { DockerService } from '../../services/docker.service';
import { NgFor, NgForOf, NgIf } from '@angular/common';

@Component({
  selector: 'app-docker-demo',
  templateUrl: './docker-demo.component.html',
  imports:[NgFor,NgForOf,NgIf]
})
export class DockerDemoComponent implements OnInit {
  dockerStatus = '';
  containers: any[] = [];

  constructor(private dockerService: DockerService) {}

  ngOnInit() {
    this.refreshContainers();
  }

  checkDocker() {
    this.dockerService.dockerCheck().subscribe({
      next: (res) => (this.dockerStatus = res.status),
      error: (err) => (this.dockerStatus = `Error: ${err.error.detail}`),
    });
  }

  createAlpineContainer() {
    this.dockerService.createContainer('my-alpine-test').subscribe({
      next: (res) => {
        alert(res.message);
        this.refreshContainers();
      },
      error: (err) => alert(`Error: ${err.error.detail}`),
    });
  }

  refreshContainers() {
    this.dockerService.listContainers(true).subscribe({
      next: (containers) => (this.containers = containers),
      error: (err) => console.error(err),
    });
  }

  stopContainer(containerId: string) {
    this.dockerService.stopContainer(containerId).subscribe({
      next: (res) => {
        alert(res.message);
        this.refreshContainers();
      },
      error: (err) => alert(`Error: ${err.error.detail}`),
    });
  }

  removeContainer(containerId: string) {
    this.dockerService.removeContainer(containerId).subscribe({
      next: (res) => {
        alert(res.message);
        this.refreshContainers();
      },
      error: (err) => alert(`Error: ${err.error.detail}`),
    });
  }
}
