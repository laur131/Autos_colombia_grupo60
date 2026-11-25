import { Component, OnInit, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Api, errMsg } from '../core/api';

@Component({
  selector: 'app-cuentas', standalone: true, imports: [FormsModule],
  template: `
  <div class="page">
    <div><span class="tag">MOCKUP G · HU-11</span><h1>Administración de Cuentas de Usuario</h1>
      <div style="font-size:12px">Cuentas de acceso del personal (Administrador / Operario). Inactivar conserva la trazabilidad histórica.</div></div>
    @if (ok) { <div class="alert ok">{{ ok }}</div> } @if (error) { <div class="alert bad">{{ error }}</div> }
    <form class="card" (ngSubmit)="guardar()">
      <h2>{{ editId ? 'Editar cuenta #' + editId : 'Nueva cuenta' }}</h2>
      <div class="row">
        <label>Nombre completo<input name="n" [(ngModel)]="f.nombre" required></label>
        <label>Documento (usuario de acceso)<input name="d" [(ngModel)]="f.documento" [disabled]="!!editId" required></label>
        <label>Teléfono<input name="t" [(ngModel)]="f.telefono"></label>
        <label>Rol<select name="r" [(ngModel)]="f.rol_id">@for (r of roles; track r.id) { <option [ngValue]="r.id">{{ r.nombre }}</option> }</select></label>
        <label>Contraseña {{ editId ? '(vacío = no cambiar)' : '' }}<input name="p" type="password" [(ngModel)]="f.password" [required]="!editId" minlength="8"></label>
        <button class="btn blue">{{ editId ? 'Guardar cambios' : 'Crear cuenta' }}</button>
        @if (editId) { <button type="button" class="btn line" (click)="nuevo()">Cancelar</button> }
      </div>
    </form>
    <div class="card">
      <table><tr><th>DOCUMENTO</th><th>NOMBRE</th><th>ROL</th><th>ESTADO</th><th>ÚLTIMO ACCESO</th><th>ACCIONES</th></tr>
        @for (u of lista; track u.id) {
          <tr><td>{{ u.documento }}</td><td>{{ u.nombre }}</td><td>{{ u.rol }}</td>
            <td [class]="u.estado_cuenta==='ACTIVO' ? 'ok' : 'bad'">{{ u.estado_cuenta }}</td><td>{{ u.ultimo_acceso || '—' }}</td>
            <td><button class="btn line" (click)="editar(u)">Editar</button>
              @if (u.estado_cuenta==='ACTIVO') { <button class="btn red" (click)="estado(u,'inactivar')">Dar de Baja</button> }
              @else { <button class="btn green" (click)="estado(u,'reactivar')">Reactivar</button> }</td></tr>
        }
      </table>
    </div>
  </div>`
})
export class CuentasComponent implements OnInit {
  private api = inject(Api);
  lista: any[] = []; roles: any[] = []; ok = ''; error = ''; editId: number | null = null;
  f: any = { nombre: '', documento: '', telefono: '', rol_id: 2, password: '' };
  ngOnInit() { this.cargar(); this.api.get<any[]>('/roles').subscribe(r => this.roles = r); }
  cargar() { this.api.get<any[]>('/usuarios').subscribe(r => this.lista = r); }
  nuevo() { this.editId = null; this.f = { nombre: '', documento: '', telefono: '', rol_id: 2, password: '' }; }
  editar(u: any) { this.editId = u.id; this.f = { nombre: u.nombre, documento: u.documento, telefono: u.telefono, rol_id: u.rol_id, password: '' }; }
  private res = (msg: string) => ({ next: () => { this.ok = msg; this.error = ''; this.nuevo(); this.cargar(); }, error: (e: any) => { this.error = errMsg(e); this.ok = ''; } });
  guardar() {
    if (this.editId) { const { documento, ...d } = this.f; if (!d.password) delete d.password; this.api.put(`/usuarios/${this.editId}`, d).subscribe(this.res('Cuenta actualizada')); }
    else this.api.post('/usuarios', this.f).subscribe(this.res('Cuenta creada'));
  }
  estado(u: any, a: string) { this.api.patch(`/usuarios/${u.id}/${a}`).subscribe(this.res(a === 'inactivar' ? 'Cuenta inactivada' : 'Cuenta reactivada')); }
}
