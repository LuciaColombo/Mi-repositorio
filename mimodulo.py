# -*- coding: utf-8 -*-
"""MiModulo.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1gw0WbaXoNYKDOrngJca8IillzeLzlppG
"""

from google.colab import drive
import pandas as pd
import numpy as np
import statsmodels.api as sm
import random
import matplotlib.pyplot as plt
from scipy.stats import t as t_distribution
from scipy.optimize import minimize_scalar
import math
from scipy.stats import norm, chi2, f, t
from sklearn.metrics import confusion_matrix, roc_curve, auc
import seaborn as sns

class ResumenNumerico:
    """Clase para calcular y almacenar un resumen numérico de un conjunto de datos."""
    def __init__(self, datos):
        self.datos = np.array(datos)
        self.res_num = {}

    def agregar_valor(self, key, value):
        self.res_num[key] = value

    def calculo_de_media(self):
        media = sum(self.datos) / len(self.datos)
        return media

    def calculo_de_mediana(self, datos=None):
      mediana = np.median(self.datos)
      return mediana

    def calculo_de_desvio_estandar(self,datos=None):
        media = self.calculo_de_media()
        n = len(self.datos)
        x =[]
        for i in range(len(self.datos)):
          x.append((i - media)**2)
          desvio_estandar = sum(x)/n

        return desvio_estandar

    def calculo_de_cuartiles(self):
        datos_ordenados = sorted(self.datos)
        mediana = self.calculo_de_mediana(datos_ordenados)
        q1 = (0+mediana)/2
        q2 = mediana
        q3 = mediana + q1

        return [q1, q2, q3]

    def generacion_resumen_numerico(self):
        """Genera un diccionario con el resumen numérico de los datos.
        :return: Diccionario con las estadísticas calculadas."""

        res_num = {
        'Media': self.calculo_de_media(),
        'Mediana': self.calculo_de_mediana(),
        'Desvio': self.calculo_de_desvio_estandar(),
        'Cuartiles': self.calculo_de_cuartiles(),
        'Mínimo': min(self.datos),
        'Máximo': max(self.datos)}

        return res_num

    def muestra_resumen(self):
        res_num =self.generacion_resumen_numerico()
        for estad, valor in res_num.items():
          print(f"{estad}: {np.round(valor,3)}")

class ResumenGrafico():
    """Clase para generar resúmenes gráficos de los datos."""
    def __init__(self, datos=None):
      if datos is not None:
        self.datos = np.array(datos)

    def generar_datos_dist_norm(self, media, desvio):
      return np.random.normal(loc=media, scale=desvio, size = self.N)

    def pdf_norm(self,x, media, desvio): #curva teorica normal
      """Calcula la función de densidad de probabilidad de una distribución normal."""
      return norm.pdf(x, media, desvio)

    def r_BS(self):
        """Genera datos con una distribución BS."""
        u = np.random.uniform(size=(self.N,))
        y = u.copy()
        ind = np.where(u > 0.5)[0]
        y[ind] = np.random.normal(0, 1, size=len(ind))
        for j in range(5):
            ind = np.where((u > j * 0.1) & (u <= (j+1) * 0.1))[0]
            y[ind] = np.random.normal(j/2 - 1, 1/10, size=len(ind))
            self.y = y
        return y

    def teorica_BS(self,x, media, desvio):
      """Calcula la densidad teórica para una distribución BS."""
      contribucion_estandar = norm.pdf(x, loc=media, scale = desvio) / 2  #termino 1: densidad de una normal teorica
      contribucion_adicional = 0  # Inicializar la variable antes del bucle for
      for j in range(5):
        media_adicional = (j/2)-1
        desvio_adicional = 1/10
        contribucion_adicional += norm.pdf(x,loc=media_adicional ,scale=desvio_adicional)

      contribucion_adicional *= (1/10)

      fBS_x = contribucion_estandar + contribucion_adicional
      return fBS_x

    def generacion_histograma(self, h):
        val_min = min(self.datos)
        val_max = max(self.datos)
        bins = np.arange(val_min, val_max, h)  #cantidad de intervalos
        if val_max > bins[-1]:
            bins = np.append(bins, bins[-1] + h)

        m = len(bins)
        histo = [0] * (m - 1)  #El histograma tiene m-1 bins
        for valor in self.datos:
            for i in range(len(bins) - 1):
                if valor == bins[0]:
                    histo[0] += 1
                    break
                elif bins[i] < valor <= bins[i + 1]:
                    histo[i] += 1
                    break
        for i in range(len(histo)):
            histo[i] /= (len(self.datos) * h)

        return bins, histo

    def evalua_histograma(self, h, x):
        bins, histo = self.generacion_histograma(h)

        res = [0] * len(x)
        for j in range(len(x)):
            if x[j] == min(self.datos):
                res[j] = histo[0]
            else:
                for i in range(len(bins) - 1):
                    if bins[i] < x[j] <= bins[i + 1]:
                        res[j] = histo[i]
                        break
        return res

    """Funciones para el calculo de los diferentes nucleos."""
    def kernel_gaussiano(self,x):     # Nucleo gaussiano estándar
        return (1 / (math.sqrt(2 * math.pi))) * math.exp(-0.5 * x**2)

    def kernel_uniforme(self, x):     # Nucleo uniforme
        valor_kernel_uniforme = []
        if -1/2 < x <= 1/2:  # Aplica la condición directamente al valor de x
            valor_kernel_uniforme.append(1)
        else:
            valor_kernel_uniforme.append(0)
        return valor_kernel_uniforme

    def kernel_cuadratico(self,x):
      valor_kernel_cuadratico = []
      if -1 < x <= 1:
          cuadratico = (3/4)*(1- x **2)
          valor_kernel_cuadratico.append(cuadratico)
      else:
          valor_kernel_cuadratico.append(0)
      return valor_kernel_cuadratico

    def kernel_triangular(self, x):
        valor_kernel_triangular = []
        triangular = 0  # Valor predeterminado
        if -1 < x <= 0:
            triangular = 1 + x
        elif 0 < x <= 1:
            triangular = 1 - x
        valor_kernel_triangular.append(triangular)
        return valor_kernel_triangular

    def kernel(self,x):
      valor = []
      n = len(x)
      if 0 < x <= max(x):
          densidad = (1/4)*x*(np.exp(-x/2))
          valor.append(densidad)
      else:
          valor.append(0)
      return valor

    """Evalúa la densidad del núcleo en los puntos x."""
    def densidad(self,x, data, h, kernel):
        n = len(data)
        densidad_estimada = []
        for valor_x in x:
          contribuciones_kernel = []
          for dato in data:
            if kernel == "examen":
              contribuciones_kernel.appen(self.kernel((dato - valor_x)/h))
            if kernel == "gaussiano":
              contribuciones_kernel.append(self.kernel_gaussiano((dato - valor_x) / h)) #paso uno a uno los datos
            elif kernel == "uniforme":
              contribuciones_kernel.append(self.kernel_uniforme((dato - valor_x) / h)) #paso uno a uno los datos
            elif kernel == "cuadratico":
              contribuciones_kernel.append(self.kernel_cuadratico((dato - valor_x) / h)) #paso uno a uno los datos
            elif kernel == "triangular":
              contribuciones_kernel.append(self.kernel_triangular((dato - valor_x) / h)) #paso uno a uno los datos

          suma_contribuciones = np.sum(contribuciones_kernel)
          densidad_estimada.append(suma_contribuciones / (n * h))
        return densidad_estimada

    def graficar_curva_roc(self, y_test, y_pred):
        """Genera y grafica la curva ROC para los datos de prueba y las predicciones del modelo de regresion logistica."""
        fpr, tpr, _ = roc_curve(y_test, y_pred)
        roc_auc = auc(fpr, tpr)
        plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'Curva ROC (área = {roc_auc:.2f})')
        plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('Tasa de Falsos Positivos')
        plt.ylabel('Tasa de Verdaderos Positivos')
        plt.title('Curva ROC')
        plt.legend(loc='lower right')
        plt.show()

    def graficar_qqplot(self, residuos):
        """Grafica el QQ-plot de los residuos."""
        sm.qqplot(residuos, line='45')
        plt.show()

    def graficar_residuos(self, predicciones, residuos):
        plt.scatter(predicciones, residuos)
        plt.xlabel('Valores Predichos')
        plt.ylabel('Residuos')
        plt.title('Gráfico de Residuos vs Valores Predichos')
        plt.show()

    def boxplot(self, x, y, datos=None):
        """Genera un gráfico boxplot."""
        if datos is None:
            raise ValueError("No se proporcionaron datos")
        plt.figure(figsize=(10, 6))
        sns.boxplot(x=x, y=y, data=datos)
        plt.title('Boxplot de {} vs {}'.format(x, y))
        plt.show()

class Regresion:

    def __init__(self,datos):
        self.datos = datos
        self.resumen_numerico = ResumenNumerico(datos)
        self.resumen_grafico = ResumenGrafico(datos)
        self.n = len(datos)
        self.coeficientes = None
        self.residuos = None

    def predecir(self, x, u=0.5): #funcion comun para regresion lineal y logistica, devuelve solo la probabilidad
        # Verificar si se han ajustado los coeficientes
        if self.coeficientes is None:
            raise Exception("Se deben ajustar los coeficientes primero.")

        #prob_pred = self.resultado.predict(x)
        prob_pred = self.resultado.predict(sm.add_constant(x))
        return prob_pred


class RegresionLineal(Regresion):
    """Clase para realizar cálculos de regresión lineal utilizando la librería statsmodels."""
    def __init__(self, datos):
        super().__init__(datos)

    def ajustar_modelo(self):
        # Convertir variables categóricas en dummies
        self.datos = pd.get_dummies(self.datos, drop_first=True) #drop_first=True para evitar multicolinealidad.

        # Separar las variables independientes (x) y la variable dependiente (y)
        x = self.datos.iloc[:, :-1].values  # Todas las columnas excepto la última
        y = self.datos.iloc[:, -1].values   # La última columna

        # Asegurarse de que y sea de tipo float
        y = y.astype(float)

        self.X = np.concatenate((np.ones((x.shape[0], 1)), x),axis=1)  # Añade una columna de unos a X para el término constante
        self.modelo = sm.OLS(y, self.X) # Defino el modelo
        self.resultado = self.modelo.fit() # Ajusto el modelo
        print(self.resultado.summary())

        if x.shape[1] == 2:  # Una columna de predicción más la constante
            print("Es una regresión lineal simple.")
        else:
            print("Es una regresión lineal múltiple.")

        self.coeficientes = self.resultado.params
        self.resumen_numerico.agregar_valor('coeficientes', self.coeficientes)
        self.residuos = y - self.resultado.predict(self.X).astype(float)
        self.resumen_numerico.agregar_valor('R-cuadrado', self.resultado.rsquared)

    def estimar_sigma(self):
        k = len(self.coeficientes) - 1
        sigma_est = np.sqrt(np.sum(self.residuos ** 2) / (self.n - self.k))
        return sigma_est

    def analizar_residuos(self):
        x = self.datos.iloc[:, :-1] # seria el x inicial, como hago para no volver a repetirlo??
        predicciones = self.predecir(x)
        residuos = self.datos.iloc[:, -1] - predicciones
        self.resumen_grafico.graficar_qqplot(residuos)
        self.resumen_grafico.graficar_residuos(predicciones, residuos)

    ## j es el índice del coeficiente para el cual deseas calcular el estadístico t de prueba, variable predictora
    def calcular_t_obs(self, j):
        if j >= len(self.coeficientes):
          raise ValueError(f"El índice {j} está fuera de los límites para los coeficientes del modelo.")
        # Estimar la varianza del error
        var_error = np.sum(self.residuos ** 2) / (self.n - len(self.coeficientes) - 1)
        # Calcular el error estándar de beta_1 (coeficiente de la variable predictora)
        se_beta1 = np.sqrt(var_error / np.sum((self.X[:, j] - np.mean(self.X[:, j])) ** 2))
        # Calcular t_obs (estadístico de prueba)
        t_obs = self.coeficientes[j] / se_beta1  # beta[1] corresponde a beta_1

        return t_obs

    def definir_region_rechazo(self, alfa):
        """Define la región de rechazo para la hipótesis H0: beta_1 = 0 dado un nivel de significancia alfa."""
        # Grados de libertad para la distribución t
        self.df_t = self.resultado.df_resid

        # Calcular el valor crítico (t_critico) para el nivel de significancia alfa
        t_critico = t_distribution.ppf(1 - alfa/2, self.df_t)

        return t_critico

    def test_hipotesis(self, j, valor_hip_nula, tipo_prueba,alfa):
        if j >= len(self.coeficientes):
          raise ValueError(f"El índice {j} está fuera de los límites para los coeficientes del modelo.")
        # Obtener el coeficiente y su error estándar
        coef = self.coeficientes[j]
        std_err = self.resultado.bse[j]

        # Calcular el estadístico t
        t_estadistico = (coef - valor_hip_nula) / std_err

        # Calcular el p-valor según el tipo de prueba
        if tipo_prueba == '=':
            p_valor = 2 * (1 - t.cdf(abs(t_estadistico), df=self.resultado.df_resid))
        elif tipo_prueba == '>':
            p_valor = 1 - t.cdf(t_estadistico, df= self.resultado.df_resid)
        elif tipo_prueba == '<':
            p_valor = t.cdf(t_estadistico, df= self.resultado.df_resid)
        else:
            raise ValueError("Tipo de prueba no soportado. Use '=', '>' o '<'.")

        return p_valor

        # Comprobar si p_valor < alfa para rechazar la hipótesis nula
        if p_valor < alfa:
            return "Hay evidencia suficiente para rechazar la hipotesis nula"  # Se rechaza H0
        else:
            return "No hay evidencia suficiente para rechazar la hipotesis nula"  # No se rechaza H0

    def intervalo_confianza(self, j, nivel_confianza):
        if j >= len(self.coeficientes):
          raise ValueError(f"El índice {j} está fuera de los límites para los coeficientes del modelo.")

        coef = self.coeficientes[j]
        std_err = self.resultado.bse[j]
        z = norm.ppf(1 - (1 - nivel_confianza) / 2)
        intervalo_inf = coef - z * std_err
        intervalo_sup = coef + z * std_err

        return intervalo_inf, intervalo_sup

    def graficar(self):

        # Calcular las predicciones usando la recta ajustada
        y_pred = self.predecir(self.X)

        # Graficar los datos de dispersión y la recta ajustada
        plt.figure(figsize=(8, 6))
        plt.scatter(self.X, self.y, color='blue', label='Datos')
        plt.plot(self.X, y_pred, color='red', label='Recta ajustada')
        plt.xlabel('X')
        plt.ylabel('Y')
        plt.title('Regresión Lineal Simple')
        plt.legend()
        plt.grid(True)
        plt.show()


class RegresionLogistica(Regresion):
    """Clase para realizar cálculos de regresión logistica utilizando la librería statsmodels."""

    def __init__(self, datos):
        super().__init__(datos)
        self.training = None
        self.testing = None

    def dividir_datos(self, test_size=0.2,seed=None):  #se destinará al subconjunto de prueba por defecto 0.2, es decir el 20% de los datos.
        np.random.seed(seed)
        perm = np.random.permutation(len(self.datos))  #permutacion de los indices en un orden aleatorio
        train_end = int((1 - test_size) * len(self.datos))  #Calcula el índice que marca el final del subconjunto de entrenamiento y el inicio del subconjunto de prueba
        self.training = self.datos.iloc[perm[:train_end]].copy()  # Asignar los datos de entrenamiento
        self.testing = self.datos.iloc[perm[train_end:]].copy()   # Asignar los datos de prueba

    def ajustar_modelo(self):
        if self.training is None or self.testing is None:
            raise Exception("Primero debe dividir los datos usando el método dividir_datos.")

        x_train = self.training.iloc[:, :-1]
        y_train = self.training.iloc[:, -1]

        # Asegurarse de que y_train esté en formato binario (0 o 1)
        if not np.all((y_train >= 0) & (y_train <= 1)):
            raise ValueError("Los valores de 'y_train' deben estar en el intervalo [0, 1].")

        X_train = sm.add_constant(x_train)
        self.modelo = sm.Logit(y_train, X_train)
        self.resultado = self.modelo.fit()
        self.coeficientes = self.resultado.params
        print(self.resultado.summary())

        y_test = self.testing.iloc[:, -1]
        x_test = sm.add_constant(self.testing.iloc[:, :-1])
        y_pred_prob =  self.predecir(x_test)
        y_pred = [1 if prob > 0.5 else 0 for prob in y_pred_prob]
        self.matriz_conf = confusion_matrix(y_test, y_pred)
        self.resumen_grafico.graficar_curva_roc(y_test, y_pred_prob)
        return self

    def graficar_matriz_confusion(self):
        plt.figure(figsize=(8, 6))
        sns.heatmap(self.matriz_conf, annot=True, cmap='Blues', fmt='g')
        plt.xlabel('Predicciones')
        plt.ylabel('Valores reales')
        plt.title('Matriz de Confusión')
        plt.show()

    def graficar(self, y_test, y_pred_prob):
        # Llamar al método de ResumenGrafico para graficar la curva ROC
        y_test = self.y_test
        y_pred = self.y_pred_prob
        grafico = ResumenGrafico.graficar_curva_roc(y_test, y_pred)

class chi_cuadrado:
    def __init__(self,datos=None):
      if datos is not None:
        self.datos = np.array(datos)

    def test(self, val_observados, prob_esperadas, alfa):
        """Paso 1: Ajustar la última probabilidad para asegurar que sumen 1"""
        prob_esperadas = np.array(prob_esperadas)
        total_prob = np.sum(prob_esperadas)
        if total_prob == 1:
            print("La suma de las probabilidades es 1")
        print("alfa=",alfa)

        """Paso 2: Calcular los valores esperados en función de las probabilidades esperadas"""
        total_observaciones = np.sum(val_observados)
        val_esperados = prob_esperadas * total_observaciones
        print(f"Valores esperados: {val_esperados}")

        """Paso 3: Calcular el estadistico Chi-cuadrado """
        chi_2 = np.sum((val_observados - val_esperados) ** 2 / val_esperados)
        print(f"Chi-cuadrado: {chi_2}")

        """Paso 4: Obtener el valor crítico de la distribución Chi-cuadrado """
        d_f = len(val_observados)-1
        val_critico = chi2.ppf(1 - alfa, d_f)
        print(f"Grados de libertad: {d_f}")
        print(f"Valor crítico percentil chi2 (α={alfa}): {val_critico}")

        """Paso 5: Calcular el p-valor para el estadístico de chi-cuadrado observado """
        p_valor = 1 - chi2.cdf(chi_2, d_f)
        print(f"p-valor: {p_valor}")

        """Paso 6: Comparar Chi-cuadrado con el valor crítico y p-valor con alfa para la conclusión """
        if chi_2 > val_critico and p_valor < alfa:
            resultado= "Rechazo la hipotesis nula"
        else:
            resultado= "No rechazo la hipotesis nula"
        print("Conclusion del test:", resultado)


class Anova():
  """Clase para realizar el test ANOVA entre dos modelos de regresión."""
  def __init__(self,datos=None):
    if datos is not None:
      self.datos = np.array(datos)

  def test(self, modelo_m, modelo_M,alfa=None):

    #Ajustar ambos modelos
    resultado_M = modelo_M.fit()
    resultado_m = modelo_m.fit()

    #Calcular RSS de ambos modelos
    RSS_m = sum(resultado_m.resid**2)
    RSS_M = sum(resultado_M.resid**2)

    #Calcular grado de libertad de ambos modelos
    gl_m = resultado_m.df_resid
    gl_M = resultado_M.df_resid
    print("Grados de libertad:",gl_m,",", gl_M)

    #Calcular el estadistico F observado
    numerador = (RSS_m - RSS_M) / (gl_m - gl_M)
    denominador = RSS_M / gl_M
    F_obs = numerador / denominador
    print(f"F-obs = {F_obs}")

    #Calcular el p-valor
    p_valor = 1-f.cdf(F_obs, gl_m-gl_M, gl_M)
    print(f"p-valor = {p_valor}")

    #Calcular el valor crítico
    F_critico = f.ppf(1 - alfa, gl_m, gl_M)
    print(f"F-crítico = {F_critico}")

  def graficar(self, x, y, datos):
    """Llamar al método de ResumenGrafico para graficar boxplot"""
    grafico = ResumenGrafico()
    grafico.boxplot(x, y, datos)