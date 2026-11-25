import { Component, OnInit, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Api, errMsg } from '../core/api';

@Component({
  selector: 'app-celdas', standalone: true, imports: [FormsModule],
  template: `
  <div class="page">
    <div><span class="tag">MOCKUP I · HU-09 / HU-13..15</span><h1>Gestión de Celdas Individuales</h1>
      <div style="font-size:12px">Estado por celda · PATCH /api/v1/celdas/{{ '{' }}id{{ '}' }}</div></div>
    @if (ok) { <div class="alert ok">{{ ok }}</div> } @if (error) { <div class="alert bad">{{ error }}</div> }
    @if (api.can('celdas.configurar')) {
      <div class="card"><span class="tag">EXCLUSIVO ROL ADMIN</span><h2 style="margin-top:6px">Capacidad máxima (aforo)</h2>
        <div class="row"><label>Carros<input type="number" [(ngModel)]="cap.capacidad_carros"></label>
          <label>Motos<input type="number" [(ngModel)]="cap.capacidad_motos"></label>
          <button class="btn" (click)="aplicarAforo()">Aplicar Cambios de Aforo</button></div>
        <div style="font-size:12px;margin-top:6px">No permite valores inferiores a la ocupación actual (RF-22).</div></div>
    }
    <div class="row">
      <label>Categoría<select [(ngModel)]="fil.categoria" (ngModelChange)="cargar()"><option value="">Todas</option><option>CARRO</option><option>MOTO</option></select></label>
      <label>Estado<select [(ngModel)]="fil.estado" (ngModelChange)="cargar()"><option value="">Todos</option><option>LIBRE</option><option>OCUPADA</option><option>BLOQUEADA</option></select></label>
    </div>
    <div class="cols">
      <div class="card" style="flex:2"><h2>{{ lista.length }} celdas</h2>
        <div class="cells">@for (c of lista; track c.id) {
          <button class="cell" [class]="'cell ' + c.estado_ocupacion" [class.off]="!c.activa" [class.sel]="sel?.id===c.id" (click)="sel=c">
            <b>{{ c.codigo }}</b><br>{{ c.activa ? c.estado_ocupacion : 'INACTIVA' }}@if (c.placa) { <br>{{ c.placa }} }</button> }</div>
        <div style="font-size:12px;margin-top:10px">Verde: libre · Rojo: ocupada · Amarillo: bloqueada · Punteada: inactiva</div></div>
      <div class="card" style="display:flex;flex-direction:column;gap:10px">
        @if (sel) {
          <h2>Celda {{ sel.codigo }}</h2>
          <div>Categoría: {{ sel.categoria }}<br>Estado: <b>{{ sel.estado_ocupacion }}</b> · {{ sel.activa ? 'Activa' : 'Inactiva' }}@if (sel.placa) { <br>Placa: {{ sel.placa }} }</div>
          @if (api.can('celdas.gestionar')) {
            <div class="row">
              @if (sel.estado_ocupacion==='LIBRE' && sel.activa) { <button class="btn line" (click)="estado('BLOQUEADA')">Bloquear</button> }
              @if (sel.estado_ocupacion==='BLOQUEADA') { <button class="btn line" (click)="estado('LIBRE')">Liberar</button> }
              @if (sel.activa) { <button class="btn red" (click)="activa('inactivar')">Inactivar</button> } @else { <button class="btn green" (click)="activa('reactivar')">Reactivar</button> }
            </div>
            <label>Nuevo código<input [(ngModel)]="nuevoCodigo"></label>
            <button class="btn blue" (click)="renombrar()">Guardar código</button>
          }
        } @else { <div>Selecciona una celda para ver su detalle.</div> }
        @if (api.can('celdas.gestionar')) {
          <hr style="width:100%"><h2>Nueva celda (RF-26)</h2>
          <div class="row"><label>Código único<input [(ngModel)]="nueva.codigo" style="width:100px"></label>
            <label>Categoría<select [(ngModel)]="nueva.categoria"><option>CARRO</option><option>MOTO</option></select></label>
            <button class="btn blue" (click)="crear()">Crear celda</button></div>
        }
      </div>
    </div>
  </div>`
})
export class CeldasComponent implements OnInit {
  api = inject(Api);
  lista: any[] = []; sel: any = null; ok = ''; error = ''; nuevoCodigo = '';
  fil = { categoria: '', estado: '' }; nueva = { codigo: '', categoria: 'CARRO' };
  cap = { capacidad_carros: 0, capacidad_motos: 0 };
  ngOnInit() { this.cargar(); this.api.get<any>('/celdas/configuracion').subscribe(c => this.cap = c); }
  cargar() { this.api.get<any[]>('/celdas', this.fil).subscribe(r => { this.lista = r; this.sel = r.find(c => c.id === this.sel?.id) ?? null; }); }
  private res = (msg: string) => ({ next: () => { this.ok = msg; this.error = ''; this.cargar(); }, error: (e: any) => { this.error = errMsg(e); this.ok = ''; } });
  estado(e: string) { this.api.patch(`/celdas/${this.sel.id}/estado`, { estado: e }).subscribe(this.res('Estado de la celda actualizado')); }
  activa(a: string) { this.api.patch(`/celdas/${this.sel.id}/${a}`).subscribe(this.res(a === 'inactivar' ? 'Celda inactivada' : 'Celda reactivada')); }
  renombrar() { this.api.put(`/celdas/${this.sel.id}`, { codigo: this.nuevoCodigo }).subscribe(this.res('Celda actualizada')); }
  crear() { this.api.post('/celdas', this.nueva).subscribe(this.res('Celda creada')); }
  aplicarAforo() { this.api.put('/celdas/configuracion', this.cap).subscribe(this.res('Aforo actualizado')); }
}
