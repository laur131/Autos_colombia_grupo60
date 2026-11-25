import { Component, inject } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { Api } from '../core/api';

@Component({
  selector: 'app-shell', standalone: true, imports: [RouterOutlet, RouterLink, RouterLinkActive],
  styles: [`.sb{width:230px;min-height:100vh;background:linear-gradient(180deg,#0b1f4d,#0e5ea8);color:#fff;padding:20px 14px;display:flex;flex-direction:column;gap:6px}
    a{color:#fff;text-decoration:none;padding:10px 12px;border-radius:10px;display:flex;flex-direction:column;font-size:14px;font-weight:600}
    a small{font-size:11px;font-weight:400;color:#bcd3f2}a.on{background:#1e88e5}`],
  template: `
  <div style="display:flex">
    <nav class="sb">
      <div style="padding:4px 8px 14px"><div style="font-size:18px;font-weight:700">AUTOS COLOMBIA</div>
        <div style="font-size:11px;color:#bcd3f2">Control de Parqueadero · v2.0</div></div>
      <div style="padding:8px;font-size:13px;border-bottom:1px solid #3a63a8;margin-bottom:8px">
        <b>{{ api.sesion()?.usuario?.nombre }} (ID: {{ api.sesion()?.usuario?.id }})</b><br>
        <span style="font-size:11px;color:#bcd3f2">Rol: {{ api.sesion()?.usuario?.rol }}</span></div>
      <div style="font-size:11px;color:#bcd3f2;padding:4px 8px">VISTAS DEL SISTEMA</div>
      @if (api.can('tablero.ver')) { <a routerLink="/tablero" routerLinkActive="on">Tablero Ocupación<small>Mockup C · HU-03</small></a> }
      @if (api.can('movimientos.registrar')) { <a routerLink="/ingreso" routerLinkActive="on">Ingreso y Rechazos<small>Mockup A · HU-01 / HU-02</small></a> }
      @if (api.can('historial.consultar')) { <a routerLink="/historial" routerLinkActive="on">Historial Auditoría<small>Mockup D · HU-04</small></a> }
      @if (api.can('titulares.gestionar')) { <a routerLink="/titulares" routerLinkActive="on">Titulares y Vehículos<small>Mockup E · HU-06 / HU-08</small></a> }
      @if (api.can('usuarios.administrar')) { <a routerLink="/cuentas" routerLinkActive="on">Cuentas de Usuario<small>Mockup G · HU-11</small></a> }
      @if (api.can('roles.administrar')) { <a routerLink="/roles" routerLinkActive="on">Roles y Permisos<small>Mockup H · HU-12</small></a> }
      @if (api.can('celdas.consultar')) { <a routerLink="/celdas" routerLinkActive="on">Celdas Individuales<small>Mockup I · HU-09 / HU-13..15</small></a> }
      <button class="btn line" style="margin-top:auto" (click)="api.logout()">Cerrar sesión</button>
    </nav>
    <main style="flex:1;min-width:0"><router-outlet /></main>
  </div>`
})
export class ShellComponent { api = inject(Api); }
