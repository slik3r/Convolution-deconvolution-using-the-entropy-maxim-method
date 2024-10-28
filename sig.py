import copy
import math
import random
import numpy as np


class Signal:
    col = 0

    def create_gauss(self, N, fd, A, n, q, count=1):
        sig_arr = []
        for i in range(0, N):
            r = 0
            for k in range(count):
                r += A[k]*math.exp(-((i/fd-n[k])/q[k])**2)
            sig_arr.append(r)
        return sig_arr

    def create_impulse(self, N, fd, A, n, q, count=1):
        sig_arr = []
        for i in range(0, N//2):
            r = 0
            for k in range(count):
                r += A[k]*math.exp(-((i/fd-n[k])/q[k])**2)
            sig_arr.append(r)
        sig_arr += [sig_arr[i] for i in range(len(sig_arr)-1, -1, -1)]
        return sig_arr


    def noise(self, val_arr, a=0):
        n = []
        for i in range(len(val_arr)):
            temp_n = 0
            for _ in range(12):
                temp_n += random.uniform(-0.5, 0.5)
            n.append(temp_n)
        es = 0
        for i in val_arr:
            es += i * i
        en = 0
        for i in n:
            en += i * i
        b = math.sqrt(a * es / en)
        n = [i * b for i in n]
        y = [val_arr[i] + n[i] for i in range(len(n))]
        return y

    def convolution(self, x, h):
        y = []
        for i in range(len(x)):
            s = 0
            for k in range(len(x)):
                if (i - k) < 0:
                    s += x[k] * h[k - i]
                else:
                    s += x[k] * h[i - k]
            y.append(s)
        return y

    def deconvolution(self, l, y, h, N, step_val):

        self.xr = [0] * N
        self.MHJ(l, y, h, N, step_val)
        self.xr = self.functionX(l, h, N)
        return self.xr


    def MHJ(self, li, yi, hi, N, step_val):#li->это Х0;yi->выходной сигнал(свертка);hi-> импульсная характеристика;N-> кол-во отсчетов;step_val-> дельта Х
        tau = 1.e-6
        li[0] = 1

        y = copy.deepcopy(li)
        b = copy.deepcopy(li)
        p = copy.deepcopy(li)
        z: float

        # функционал среднеквадратичного отклонения
        fi = self.functional(li, N, hi, yi)##li->это Х0;yi->выходной сигнал(свертка);hi-> импульсная характеристика;N-> кол-во отсчетов;step_val-> дельта Х

        ps = 0
        bs = 1
        fb = fi

        k = step_val
        j = 0
        calc = 0
        while True:
            calc += 1
            li[j] = y[j] + k
            z = self.functional(li, N, hi, yi)
            if z >= fi:
                li[j] = y[j] - k
                z = self.functional(li, N, hi, yi)
                if z < fi:
                    y[j] = li[j]
                else:
                    li[j] = y[j]
            else:
                y[j] = li[j]

            fi = self.functional(li, N, hi, yi)
            if j < (N-1):
                j += 1
                continue
            if (fi+(1.e-3)) >= fb:
                if ps == 1 and bs == 0:
                    for i in range(N):
                        p[i] = y[i] = li[i] = b[i]
                    z = self.functional(li, N, hi, yi)
                    bs = 1
                    ps = 0
                    fi = z
                    fb = z
                    j = 0
                    continue
                k /= 10
                if k < tau:
                    break
                j = 0
                continue
            for i in range(N):
                p[i] = 2 * y[i] - b[i]
                b[i] = y[i]
                li[i] = p[i]
                y[i] = li[i]
            z = self.functional(li, N, hi, yi)
            fb = fi
            ps = 1
            bs = 0
            fi = z
            j = 0
        #for i in range(N):
        #    li[i] = p[i]
        #print(self.col)
        return fb

    def functionX(self, l, h, N):#l->это Х0;h-> импульсная характеристика;N-> кол-во отсчетов
        xi = []
        for i in range(N):
            s = 0
            for j in range(N):
                if (i - j) < 0:
                    s += l[j] * h[j - i]
                else:
                    s += l[j] * h[i - j]
            xi.append(math.exp(-1-s))
        self.xr = xi
#self.col += 1
        return xi


    # функционал среднеквадратичного отклонения
    def functional(self, li, N, h, y):#li->это Х0;y->выходной сигнал(свертка);h-> импульсная характеристика;N-> кол-во отсчетов;step_val-> дельта Х
        z = 0
        xi = self.functionX(li, h, N)
        yi = []
        for i in range(N):
            s = 0
            for j in range(N):
                if (i-j) < 0:
                    s += xi[j] * h[j-i]
                else:
                    s += xi[j] * h[i-j]
            yi.append(s)
            z += (y[i] - yi[i])**2# функционал среднеквадратичного отклонения

        return z

    def energy_delta(self, x, y):
        self.ed = 0
        for val1, val2 in zip(x, y):
            self.ed += (val1-val2)**2
        return self.ed
