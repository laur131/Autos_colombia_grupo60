import { Component, OnInit, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Api, errMsg } from '../core/api';

@Component({
  selector: 'app-titulares', standalone: true, imports: [FormsModule],
  template: `
  <div class="page">
    <div><span class="tag">MOCKUP E · HU-06 / HU-08</span><h1>Titulares y Vehículos</h1>
      <div style="font-size:12px">La baja lógica (INACTIVO) de un titular bloquea el ingreso de sus vehículos vinculados.</div></div>
    @if (ok) { <div class="alert ok">{{ ok }}</div> } @if (error) { <div class="alert bad">{{ error }}</div> }
    <div class="cols">
      <form class="card" (ngSubmit)="crearTitular()"><h2>Nuevo titular (RF-15)</h2>
        <div class="row"><label>Nombres<input name="n" [(ngModel)]="t.nombres" required></label><label>Apellidos<input name="a" [(ngModel)]="t.apellidos" required></label></div>
        <div class="row" style="margin-top:8px"><label>Documento<input name="d" [(ngModel)]="t.documento" required></label><label>Teléfono<input name="tel" [(ngModel)]="t.telefono"></label>
          <button class="btn blue">Crear titular</button></div></form>
      <form class="card" (ngSubmit)="crearVeh()"><h2>Vincular vehículo (RF-19)</h2>
        <div class="row"><label>Placa<input name="p" [(ngModel)]="v.placa" required style="width:110px"></label>
          <label>Tipo<select name="tp" [(ngModel)]="v.tipo"><option>CARRO</option><option>MOTO</option></select></label>
          <label>Marca<input name="m" [(ngModel)]="v.marca" style="width:110px"></label><label>Color<input name="c" [(ngModel)]="v.color" style="width:90px"></label></div>
        <div class="row" style="margin-top:8px"><label>Titular<select name="ti" [(ngModel)]="v.titular_id">
          @for (x of lista; track x.id) { <option [ngValue]="x.id">{{ x.nombres }} {{ x.apellidos }}</option> }</select></label>
          <button class="btn blue">Vincular</button></div></form>
    </div>
    <div class="card">
      <h2>Mensualidad (vigencia del vehículo)</h2>
      <div class="row"><label>Vehículo (ID)<input type="number" [(ngModel)]="m.vehiculo_id" style="width:100px"></label>
        <label>Inicio<input type="date" [(ngModel)]="m.fecha_inicio"></label><label>Fin<input type="date" [(ngModel)]="m.fecha_fin"></label>
        <label>Valor<input type="number" [(ngModel)]="m.valor" style="width:120px"></label><button class="btn line" (click)="crearMens()">Registrar mensualidad</button></div>
    </div>
    <div class="card">
      <div class="row"><h2 class="grow">Directorio de titulares</h2><input placeholder="Buscar por documento o nombre" [(ngModel)]="q" (ngModelChange)="cargar()" style="width:280px"></div>
      <table><tr><th>DOCUMENTO</th><th>NOMBRE COMPLETO</th><th>VEHÍCULOS VINCULADOS (FK)</th><th>ESTADO</th><th>ACCIONES (BAJA LÓGICA)</th></tr>
        @for (x of lista; track x.id) {
          <tr><td>{{ x.documento }}</td><td>{{ x.nombres }} {{ x.apellidos }}</td>
            <td>@for (ve of x.vehiculos; track ve.id) { <span class="tag">{{ ve.placa }} #{{ ve.id }} ({{ ve.tipo }})</span> }</td>
            <td [class]="x.estado==='ACTIVO' ? 'ok' : 'bad'">{{ x.estado }}</td>
            <td>@if (x.estado==='ACTIVO') { <button class="btn red" (click)="estado(x,'inactivar')">Dar de Baja</button> }
                @else { <button class="btn green" (click)="estado(x,'reactivar')">Reactivar</button> }</td></tr>
        }
      </table>
    </div>
  </div>`
})
export class TitularesComponent implements OnInit {
  private api = inject(Api);
  lista: any[] = []; q = ''; ok = ''; error = '';
  t: any = { nombres: '', apellidos: '', documento: '', telefono: '' };
  v: any = { placa: '', tipo: 'CARRO', marca: '', color: '', titular_id: null };
  m: any = { vehiculo_id: null, fecha_inicio: '', fecha_fin: '', valor: 250000 };
  ngOnInit() { this.cargar(); }
  private res = (msg: string) => ({ next: () => { this.ok = msg; this.error = ''; this.cargar(); }, error: (e: any) => { this.error = errMsg(e); this.ok = ''; } });
  cargar() { this.api.get<any[]>('/titulares', { q: this.q }).subscribe(r => this.lista = r); }
  crearTitular() { this.api.post('/titulares', this.t).subscribe(this.res('Titular creado')); }
  crearVeh() { this.api.post('/vehiculos', this.v).subscribe(this.res('Vehículo vinculado')); }
  crearMens() { this.api.post('/mensualidades', this.m).subscribe(this.res('Mensualidad registrada')); }
  estado(x: any, accion: string) { this.api.patch(`/titulares/${x.id}/${accion}`).subscribe(this.res(accion === 'inactivar' ? 'Titular dado de baja' : 'Titular reactivado')); }
}
