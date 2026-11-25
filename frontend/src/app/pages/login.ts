import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { Api, errMsg } from '../core/api';

@Component({
  selector: 'app-login', standalone: true, imports: [FormsModule],
  template: `
  <div style="display:flex;min-height:100vh">
    <div style="flex:1;background:linear-gradient(160deg,#0b1f4d,#0e5ea8);color:#fff;padding:64px;display:flex;flex-direction:column;justify-content:center;gap:12px">
      <div style="font-size:40px;font-weight:700">AUTOS COLOMBIA</div>
      <div style="font-size:18px;color:#cfe1fa">Control de Parqueadero · v2.0</div>
      <div style="color:#bcd3f2;max-width:380px">Acceso para personal administrativo y operativo de la Sede Principal, Bogotá D.C.</div>
    </div>
    <div style="flex:1;display:flex;align-items:center;justify-content:center">
      <form class="card" style="width:380px;display:flex;flex-direction:column;gap:14px;padding:28px" (ngSubmit)="entrar()">
        <h1>Inicio de sesión</h1>
        <label>Documento de identidad<input name="doc" [(ngModel)]="documento" autocomplete="username" required></label>
        <label>Contraseña<input name="pw" type="password" [(ngModel)]="password" autocomplete="current-password" required></label>
        <button class="btn" [disabled]="cargando">Iniciar sesión</button>
        @if (error) { <div class="alert bad">{{ error }}</div> }
        <div style="font-size:12px;color:#4a5578;text-align:center">Tras 5 intentos fallidos la cuenta se bloquea 15 min.</div>
      </form>
    </div>
  </div>`
})
export class LoginComponent {
  private api = inject(Api); private router = inject(Router);
  documento = ''; password = ''; error = ''; cargando = false;
  entrar() {
    this.cargando = true; this.error = '';
    this.api.login(this.documento, this.password).subscribe({
      next: () => this.router.navigate(['/']),
      error: e => { this.error = errMsg(e); this.cargando = false; }
    });
  }
}
