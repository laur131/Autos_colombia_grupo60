import { Component, OnInit, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Api, errMsg } from '../core/api';

@Component({
  selector: 'app-historial', standalone: true, imports: [FormsModule],
  template: `
  <div class="page">
    <div><span class="tag">MOCKUP D · HU-04</span><h1>Historial de Auditoría y Trazabilidad Operativa</h1></div>
    <div class="card row">
      <label>Placa<input [(ngModel)]="f.placa"></label>
      <label>Desde<input type="date" [(ngModel)]="f.desde"></label>
      <label>Hasta<input type="date" [(ngModel)]="f.hasta"></label>
      <label>Estado<select [(ngModel)]="f.estado"><option value="">Todos</option><option>ABIERTO</option><option>CERRADO</option></select></label>
      <button class="btn blue" (click)="buscar()">Filtrar</button>
      <button class="btn line" (click)="f={placa:'',desde:'',hasta:'',estado:''}; buscar()">Limpiar</button>
    </div>
    @if (error) { <div class="alert bad">{{ error }}</div> }
    <div class="card" style="overflow-x:auto">
      <table><tr><th>ID</th><th>PLACA</th><th>ENTRADA</th><th>OPERARIO INGRESO (operario_id)</th><th>SALIDA</th><th>OPERARIO CIERRE (operario_cierre_id)</th><th>ESTADO</th><th>NOVEDADES</th></tr>
        @for (m of filas; track m.id) {
          <tr><td>MOV-{{ m.id }}</td><td><b>{{ m.placa }}</b><br><span class="tag">{{ m.tipo }}</span></td>
            <td>{{ m.fecha_entrada.replace('T',' ') }}</td><td>{{ m.operario_ingreso }} (ID: {{ m.operario_id }})</td>
            <td>{{ m.fecha_salida ? m.fecha_salida.replace('T',' ') : 'En estancia…' }}</td>
            <td>{{ m.operario_cierre ? m.operario_cierre + ' (ID: ' + m.operario_cierre_id + ')' : 'Pendiente cierre' }}</td>
            <td [class]="m.estado==='ABIERTO' ? 'warn' : 'ok'">{{ m.estado }}</td>
            <td>Entrada: {{ m.observacion_entrada || 'Sin novedad' }} | Salida: {{ m.observacion_salida || 'Pendiente' }}
              @if (m.novedades) { <br><i>{{ m.novedades }}</i> }</td></tr>
        }
      </table>
      <p style="font-size:12px">Mostrando {{ filas.length }} registros</p>
    </div>
  </div>`
})
export class HistorialComponent implements OnInit {
  private api = inject(Api);
  f = { placa: '', desde: '', hasta: '', estado: '' }; filas: any[] = []; error = '';
  ngOnInit() { this.buscar(); }
  buscar() { this.api.get<any[]>('/movimientos', this.f).subscribe({ next: r => { this.filas = r; this.error = ''; }, error: e => this.error = errMsg(e) }); }
}
