import { Component, OnInit, inject } from '@angular/core';
import { Api, errMsg } from '../core/api';

@Component({
  selector: 'app-roles', standalone: true,
  template: `
  <div class="page">
    <div><span class="tag">MOCKUP H · HU-12</span><h1>Roles y Permisos</h1>
      <div style="font-size:12px">Matriz de acceso por rol (RBAC) · PUT /api/v1/roles/{{ '{' }}id{{ '}' }}/permisos</div></div>
    @if (ok) { <div class="alert ok">{{ ok }}</div> } @if (error) { <div class="alert bad">{{ error }}</div> }
    <div class="cols">
      @for (r of roles; track r.id) {
        <div class="card"><h2>{{ r.nombre }}</h2><div style="font-size:26px;font-weight:700">{{ r.usuarios }} usuarios</div></div>
      }
    </div>
    <div class="card" style="overflow-x:auto">
      <table><tr><th>PERMISO</th>@for (r of roles; track r.id) { <th>{{ r.nombre }}</th> }</tr>
        @for (p of permisos; track p.id) {
          <tr><td>{{ p.descripcion }}<br><span class="tag">{{ p.codigo }}</span></td>
            @for (r of roles; track r.id) {
              <td><label style="flex-direction:row;align-items:center;gap:6px">
                <input type="checkbox" [checked]="r.permisos.includes(p.codigo)" (change)="alternar(r, p.codigo)">
                <span [class]="r.permisos.includes(p.codigo) ? 'ok' : 'bad'">{{ r.permisos.includes(p.codigo) ? 'Permitido' : 'Denegado' }}</span></label></td>
            }</tr>
        }
      </table>
    </div>
    <div class="row">@for (r of roles; track r.id) { <button class="btn" (click)="guardar(r)">Guardar permisos de {{ r.nombre }}</button> }</div>
  </div>`
})
export class RolesComponent implements OnInit {
  private api = inject(Api);
  roles: any[] = []; permisos: any[] = []; ok = ''; error = '';
  ngOnInit() { this.api.get<any[]>('/roles').subscribe(r => this.roles = r); this.api.get<any[]>('/permisos').subscribe(p => this.permisos = p); }
  alternar(r: any, cod: string) { r.permisos = r.permisos.includes(cod) ? r.permisos.filter((c: string) => c !== cod) : [...r.permisos, cod]; }
  guardar(r: any) {
    this.api.put<any>(`/roles/${r.id}/permisos`, { permisos: r.permisos }).subscribe({
      next: n => { Object.assign(r, n); this.ok = `Permisos de ${r.nombre} actualizados (aplican en la siguiente petición)`; this.error = ''; },
      error: e => { this.error = errMsg(e); this.ok = ''; this.ngOnInit(); }
    });
  }
}
