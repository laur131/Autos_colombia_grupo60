import { Component, OnDestroy, OnInit, inject } from '@angular/core';
import { RouterLink } from '@angular/router';
import { Api, errMsg } from '../core/api';

@Component({
  selector: 'app-tablero', standalone: true, imports: [RouterLink],
  template: `
  <div class="page">
    <div><span class="tag">MOCKUP C · HU-03</span><h1>Tablero de Ocupación en Tiempo Real</h1></div>
    @if (error) { <div class="alert bad">{{ error }}</div> }
    @if (o) {
      <div class="cols">
        @for (c of cats; track c.k) {
          <div class="card">
            <h2>{{ c.n }}</h2>
            <div style="font-size:34px;font-weight:700">{{ o[c.k].ocupados }} <span style="font-size:16px;font-weight:400">/ {{ o[c.k].capacidad }} ocupados</span></div>
            <div class="bar" [class.full]="o[c.k].lleno"><i [style.width.%]="o[c.k].porcentaje"></i></div>
            <p>{{ o[c.k].libres }} cupos libres · ocupación {{ o[c.k].porcentaje }}%
              @if (o[c.k].lleno) { <span class="bad"> · Categoría llena: ingresos bloqueados (409)</span> }</p>
          </div>
        }
      </div>
      <div class="card">
        <div class="row"><h2 class="grow">Vehículos en estancia activa</h2>
          @if (api.can('movimientos.registrar')) { <a class="btn blue" routerLink="/ingreso">Registrar ingreso / salida</a> }</div>
        <table><tr><th>PLACA</th><th>CATEGORÍA</th><th>CELDA</th><th>TITULAR</th><th>HORA INGRESO</th><th>OPERARIO APERTURA</th></tr>
          @for (e of o.estancias; track e.id) {
            <tr><td><b>{{ e.placa }}</b></td><td><span class="tag">{{ e.tipo }}</span></td><td>{{ e.celda }}</td><td>{{ e.titular }}</td>
              <td>{{ e.fecha_entrada.replace('T',' ') }}</td><td>{{ e.operario_ingreso }} (ID: {{ e.operario_id }})</td></tr>
          }
        </table>
      </div>
    }
  </div>`
})
export class TableroComponent implements OnInit, OnDestroy {
  api = inject(Api);
  o: any = null; error = ''; private t: any;
  cats = [{ k: 'carros', n: 'Vehículos tipo Carro' }, { k: 'motos', n: 'Motocicletas' }];
  ngOnInit() { this.cargar(); this.t = setInterval(() => this.cargar(), 5000); }
  ngOnDestroy() { clearInterval(this.t); }
  cargar() { this.api.get('/movimientos/ocupacion').subscribe({ next: r => { this.o = r; this.error = ''; }, error: e => this.error = errMsg(e) }); }
}
