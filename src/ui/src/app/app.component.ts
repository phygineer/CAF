import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { LanguageSelectorComponent } from "./components/language-selector/language-selector.component";
import { DockerDemoComponent } from "./components/docker-demo/docker-demo.component";

@Component({
  selector: 'app-root',
  imports: [LanguageSelectorComponent, DockerDemoComponent],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent {
  title = 'ui';
}
