import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Api, errMsg } from '../core/api';

@Component({
  selector: 'app-ingreso', standalone: true, imports: [FormsModule],
  template: `
  <div class="page">
    <div><span class="tag">MOCKUP A · HU-01 / HU-02</span><h1>Registro de Ingreso, Salida y Novedades</h1></div>
    <div class="row">
      <button class="btn" [class.line]="modo!=='ingreso'" (click)="modo='ingreso'; limpiar()">Ingreso</button>
      <button class="btn" [class.line]="modo!=='salida'" (click)="modo='salida'; limpiar()">Salida</button>
    </div>
    <div class="card">
      <div class="row">
        <label class="grow">Placa del vehículo *<input [(ngModel)]="placa" placeholder="XYZ789" style="text-transform:uppercase"></label>
        <button class="btn blue" (click)="consultar()">Consultar</button>
      </div>
      @if (info) { <p style="margin:12px 0 0">{{ info }}</p> }
      <label style="margin-top:12px">{{ modo==='ingreso' ? 'Observaciones de recepción (opcional)' : 'Novedades de entrega (obligatorio)' }}
        <textarea rows="3" maxlength="500" [(ngModel)]="obs"></textarea></label>
      <div class="row" style="margin-top:12px">
        <button class="btn" (click)="enviar()">{{ modo==='ingreso' ? 'Registrar ingreso' : 'Registrar salida' }}</button></div>
    </div>
    @if (ok) { <div class="alert ok"><b>{{ ok }}</b></div> }
    @if (error) { <div class="alert bad"><b>Rechazado:</b> {{ error }}</div> }
    <div class="card">
      <h2>Registrar novedad sobre un movimiento (RF-13)</h2>
      <div class="row">
        <label>ID movimiento<input type="number" [(ngModel)]="movId" style="width:120px"></label>
        <label class="grow">Descripción<input [(ngModel)]="novedad"></label>
        <button class="btn line" (click)="addNovedad()">Guardar novedad</button></div>
    </div>
  </div>`
})
export class IngresoComponent {
  private api = inject(Api);
  modo: 'ingreso' | 'salida' = 'ingreso';
  placa = ''; obs = ''; info = ''; ok = ''; error = ''; movId: number | null = null; novedad = '';
  limpiar() { this.ok = this.error = this.info = ''; }
  consultar() {
    this.limpiar();
    const url = this.modo === 'ingreso' ? `/vehiculos/${this.placa}` : `/movimientos/abiertos/${this.placa}`;
    this.api.get<any>(url).subscribe({
      next: v => this.info = this.modo === 'ingreso'
        ? `${v.tipo} · ${v.marca ?? ''} ${v.color ?? ''} · Titular: ${v.titular} (${v.titular_estado}) · Mensualidad ${v.mensualidad ? 'vigente hasta ' + v.mensualidad.fecha_fin : 'VENCIDA'}`
        : `Movimiento #${v.id} · celda ${v.celda} · entró ${v.fecha_entrada.replace('T', ' ')} · operario ${v.operario_ingreso}`,
      error: e => this.error = errMsg(e)
    });
  }
  enviar() {
    this.ok = this.error = '';
    const req = this.modo === 'ingreso'
      ? this.api.post<any>('/movimientos/ingresos', { placa: this.placa, observacion: this.obs })
      : this.api.post<any>('/movimientos/salidas', { placa: this.placa, observacion: this.obs });
    req.subscribe({
      next: m => { this.ok = this.modo === 'ingreso' ? `Ingreso autorizado · movimiento #${m.id} · celda ${m.celda}` : `Salida registrada · movimiento #${m.id} CERRADO · celda ${m.celda} liberada`; this.obs = ''; },
      error: e => this.error = errMsg(e)
    });
  }
  addNovedad() {
    this.ok = this.error = '';
    this.api.post(`/movimientos/${this.movId}/novedades`, { descripcion: this.novedad }).subscribe({
      next: () => { this.ok = 'Novedad registrada'; this.novedad = ''; }, error: e => this.error = errMsg(e) });
  }
}
