var Px = Object.create;
var { getPrototypeOf: Ax, defineProperty: UN, getOwnPropertyNames: Lx } = Object;
var Ox = Object.prototype.hasOwnProperty;
var D6 = (Q, J, Y) => {
  Y = Q != null ? Px(Ax(Q)) : {};
  let W = J || !Q || !Q.__esModule ? UN(Y, "default", { value: Q, enumerable: !0 }) : Y;
  for (let K of Lx(Q))
    if (!Ox.call(W, K))
      UN(W, K, {
        get: () => Q[K],
        enumerable: !0
      });
  return W;
};
var $6 = (Q, J) => () => (J || Q((J = { exports: {} }).exports, J), J.exports);
var sY = (Q, J) => {
  for (var Y in J)
    UN(Q, Y, {
      get: J[Y],
      enumerable: !0,
      configurable: !0,
      set: (W) => J[Y] = () => W
    });
};

// node_modules/react/cjs/react.development.js
var LQ = $6((wx, V5) => {
  (function() {
    if (typeof __REACT_DEVTOOLS_GLOBAL_HOOK__ !== "undefined" && typeof __REACT_DEVTOOLS_GLOBAL_HOOK__.registerInternalModuleStart === "function")
      __REACT_DEVTOOLS_GLOBAL_HOOK__.registerInternalModuleStart(new Error);
    var Q = "18.3.1", J = Symbol.for("react.element"), Y = Symbol.for("react.portal"), W = Symbol.for("react.fragment"), K = Symbol.for("react.strict_mode"), z = Symbol.for("react.profiler"), N = Symbol.for("react.provider"), F = Symbol.for("react.context"), L = Symbol.for("react.forward_ref"), w = Symbol.for("react.suspense"), D = Symbol.for("react.suspense_list"), R = Symbol.for("react.memo"), V = Symbol.for("react.lazy"), g = Symbol.for("react.offscreen"), s = Symbol.iterator, i = "@@iterator";
    function F0(A) {
      if (A === null || typeof A !== "object")
        return null;
      var j = s && A[s] || A[i];
      if (typeof j === "function")
        return j;
      return null;
    }
    var r = {
      current: null
    }, J0 = {
      transition: null
    }, l = {
      current: null,
      isBatchingLegacy: !1,
      didScheduleLegacyUpdate: !1
    }, t = {
      current: null
    }, $0 = {}, M0 = null;
    function c0(A) {
      M0 = A;
    }
    $0.setExtraStackFrame = function(A) {
      M0 = A;
    }, $0.getCurrentStack = null, $0.getStackAddendum = function() {
      var A = "";
      if (M0)
        A += M0;
      var j = $0.getCurrentStack;
      if (j)
        A += j() || "";
      return A;
    };
    var I0 = !1, p = !1, o = !1, Y0 = !1, A0 = !1, P0 = {
      ReactCurrentDispatcher: r,
      ReactCurrentBatchConfig: J0,
      ReactCurrentOwner: t
    };
    P0.ReactDebugCurrentFrame = $0, P0.ReactCurrentActQueue = l;
    function Y1(A) {
      {
        for (var j = arguments.length, x = new Array(j > 1 ? j - 1 : 0), m = 1;m < j; m++)
          x[m - 1] = arguments[m];
        W0("warn", A, x);
      }
    }
    function N0(A) {
      {
        for (var j = arguments.length, x = new Array(j > 1 ? j - 1 : 0), m = 1;m < j; m++)
          x[m - 1] = arguments[m];
        W0("error", A, x);
      }
    }
    function W0(A, j, x) {
      {
        var m = P0.ReactDebugCurrentFrame, e = m.getStackAddendum();
        if (e !== "")
          j += "%s", x = x.concat([e]);
        var T0 = x.map(function(O0) {
          return String(O0);
        });
        T0.unshift("Warning: " + j), Function.prototype.apply.call(console[A], console, T0);
      }
    }
    var v0 = {};
    function n1(A, j) {
      {
        var x = A.constructor, m = x && (x.displayName || x.name) || "ReactClass", e = m + "." + j;
        if (v0[e])
          return;
        N0("Can't call %s on a component that is not yet mounted. This is a no-op, but it might indicate a bug in your application. Instead, assign to `this.state` directly or define a `state = {};` class property with the desired state in the %s component.", j, m), v0[e] = !0;
      }
    }
    var g1 = {
      isMounted: function(A) {
        return !1;
      },
      enqueueForceUpdate: function(A, j, x) {
        n1(A, "forceUpdate");
      },
      enqueueReplaceState: function(A, j, x, m) {
        n1(A, "replaceState");
      },
      enqueueSetState: function(A, j, x, m) {
        n1(A, "setState");
      }
    }, s1 = Object.assign, _1 = {};
    Object.freeze(_1);
    function U1(A, j, x) {
      this.props = A, this.context = j, this.refs = _1, this.updater = x || g1;
    }
    U1.prototype.isReactComponent = {}, U1.prototype.setState = function(A, j) {
      if (typeof A !== "object" && typeof A !== "function" && A != null)
        throw new Error("setState(...): takes an object of state variables to update or a function which returns an object of state variables.");
      this.updater.enqueueSetState(this, A, j, "setState");
    }, U1.prototype.forceUpdate = function(A) {
      this.updater.enqueueForceUpdate(this, A, "forceUpdate");
    };
    {
      var x0 = {
        isMounted: ["isMounted", "Instead, make sure to clean up subscriptions and pending requests in componentWillUnmount to prevent memory leaks."],
        replaceState: ["replaceState", "Refactor your code to use setState instead (see https://github.com/facebook/react/issues/3236)."]
      }, N6 = function(A, j) {
        Object.defineProperty(U1.prototype, A, {
          get: function() {
            Y1("%s(...) is deprecated in plain JavaScript React classes. %s", j[0], j[1]);
            return;
          }
        });
      };
      for (var C6 in x0)
        if (x0.hasOwnProperty(C6))
          N6(C6, x0[C6]);
    }
    function o1() {}
    o1.prototype = U1.prototype;
    function f1(A, j, x) {
      this.props = A, this.context = j, this.refs = _1, this.updater = x || g1;
    }
    var E6 = f1.prototype = new o1;
    E6.constructor = f1, s1(E6, U1.prototype), E6.isPureReactComponent = !0;
    function x1() {
      var A = {
        current: null
      };
      return Object.seal(A), A;
    }
    var l0 = Array.isArray;
    function i1(A) {
      return l0(A);
    }
    function Z0(A) {
      {
        var j = typeof Symbol === "function" && Symbol.toStringTag, x = j && A[Symbol.toStringTag] || A.constructor.name || "Object";
        return x;
      }
    }
    function F6(A) {
      try {
        return C1(A), !1;
      } catch (j) {
        return !0;
      }
    }
    function C1(A) {
      return "" + A;
    }
    function v1(A) {
      if (F6(A))
        return N0("The provided key is an unsupported type %s. This value must be coerced to a string before before using it here.", Z0(A)), C1(A);
    }
    function h6(A, j, x) {
      var m = A.displayName;
      if (m)
        return m;
      var e = j.displayName || j.name || "";
      return e !== "" ? x + "(" + e + ")" : x;
    }
    function c8(A) {
      return A.displayName || "Context";
    }
    function p6(A) {
      if (A == null)
        return null;
      if (typeof A.tag === "number")
        N0("Received an unexpected object in getComponentNameFromType(). This is likely a bug in React. Please file an issue.");
      if (typeof A === "function")
        return A.displayName || A.name || null;
      if (typeof A === "string")
        return A;
      switch (A) {
        case W:
          return "Fragment";
        case Y:
          return "Portal";
        case z:
          return "Profiler";
        case K:
          return "StrictMode";
        case w:
          return "Suspense";
        case D:
          return "SuspenseList";
      }
      if (typeof A === "object")
        switch (A.$$typeof) {
          case F:
            var j = A;
            return c8(j) + ".Consumer";
          case N:
            var x = A;
            return c8(x._context) + ".Provider";
          case L:
            return h6(A, A.render, "ForwardRef");
          case R:
            var m = A.displayName || null;
            if (m !== null)
              return m;
            return p6(A.type) || "Memo";
          case V: {
            var e = A, T0 = e._payload, O0 = e._init;
            try {
              return p6(O0(T0));
            } catch (m0) {
              return null;
            }
          }
        }
      return null;
    }
    var k8 = Object.prototype.hasOwnProperty, q8 = {
      key: !0,
      ref: !0,
      __self: !0,
      __source: !0
    }, W8, d6, A6;
    A6 = {};
    function RQ(A) {
      if (k8.call(A, "ref")) {
        var j = Object.getOwnPropertyDescriptor(A, "ref").get;
        if (j && j.isReactWarning)
          return !1;
      }
      return A.ref !== void 0;
    }
    function R8(A) {
      if (k8.call(A, "key")) {
        var j = Object.getOwnPropertyDescriptor(A, "key").get;
        if (j && j.isReactWarning)
          return !1;
      }
      return A.key !== void 0;
    }
    function WQ(A, j) {
      var x = function() {
        if (!W8)
          W8 = !0, N0("%s: `key` is not a prop. Trying to access it will result in `undefined` being returned. If you need to access the same value within the child component, you should pass it as a different prop. (https://reactjs.org/link/special-props)", j);
      };
      x.isReactWarning = !0, Object.defineProperty(A, "key", {
        get: x,
        configurable: !0
      });
    }
    function l6(A, j) {
      var x = function() {
        if (!d6)
          d6 = !0, N0("%s: `ref` is not a prop. Trying to access it will result in `undefined` being returned. If you need to access the same value within the child component, you should pass it as a different prop. (https://reactjs.org/link/special-props)", j);
      };
      x.isReactWarning = !0, Object.defineProperty(A, "ref", {
        get: x,
        configurable: !0
      });
    }
    function p8(A) {
      if (typeof A.ref === "string" && t.current && A.__self && t.current.stateNode !== A.__self) {
        var j = p6(t.current.type);
        if (!A6[j])
          N0('Component "%s" contains the string ref "%s". Support for string refs will be removed in a future major release. This case cannot be automatically converted to an arrow function. We ask you to manually fix this case by using useRef() or createRef() instead. Learn more about using refs safely here: https://reactjs.org/link/strict-mode-string-ref', j, A.ref), A6[j] = !0;
      }
    }
    var d8 = function(A, j, x, m, e, T0, O0) {
      var m0 = {
        $$typeof: J,
        type: A,
        key: j,
        ref: x,
        props: O0,
        _owner: T0
      };
      if (m0._store = {}, Object.defineProperty(m0._store, "validated", {
        configurable: !1,
        enumerable: !1,
        writable: !0,
        value: !1
      }), Object.defineProperty(m0, "_self", {
        configurable: !1,
        enumerable: !1,
        writable: !1,
        value: m
      }), Object.defineProperty(m0, "_source", {
        configurable: !1,
        enumerable: !1,
        writable: !1,
        value: e
      }), Object.freeze)
        Object.freeze(m0.props), Object.freeze(m0);
      return m0;
    };
    function jQ(A, j, x) {
      var m, e = {}, T0 = null, O0 = null, m0 = null, P1 = null;
      if (j != null) {
        if (RQ(j))
          O0 = j.ref, p8(j);
        if (R8(j))
          v1(j.key), T0 = "" + j.key;
        m0 = j.__self === void 0 ? null : j.__self, P1 = j.__source === void 0 ? null : j.__source;
        for (m in j)
          if (k8.call(j, m) && !q8.hasOwnProperty(m))
            e[m] = j[m];
      }
      var m1 = arguments.length - 2;
      if (m1 === 1)
        e.children = x;
      else if (m1 > 1) {
        var e1 = Array(m1);
        for (var Q6 = 0;Q6 < m1; Q6++)
          e1[Q6] = arguments[Q6 + 2];
        if (Object.freeze)
          Object.freeze(e1);
        e.children = e1;
      }
      if (A && A.defaultProps) {
        var q6 = A.defaultProps;
        for (m in q6)
          if (e[m] === void 0)
            e[m] = q6[m];
      }
      if (T0 || O0) {
        var R6 = typeof A === "function" ? A.displayName || A.name || "Unknown" : A;
        if (T0)
          WQ(e, R6);
        if (O0)
          l6(e, R6);
      }
      return d8(A, T0, O0, m0, P1, t.current, e);
    }
    function Q0(A, j) {
      var x = d8(A.type, j, A.ref, A._self, A._source, A._owner, A.props);
      return x;
    }
    function D0(A, j, x) {
      if (A === null || A === void 0)
        throw new Error("React.cloneElement(...): The argument must be a React element, but you passed " + A + ".");
      var m, e = s1({}, A.props), T0 = A.key, O0 = A.ref, m0 = A._self, P1 = A._source, m1 = A._owner;
      if (j != null) {
        if (RQ(j))
          O0 = j.ref, m1 = t.current;
        if (R8(j))
          v1(j.key), T0 = "" + j.key;
        var e1;
        if (A.type && A.type.defaultProps)
          e1 = A.type.defaultProps;
        for (m in j)
          if (k8.call(j, m) && !q8.hasOwnProperty(m))
            if (j[m] === void 0 && e1 !== void 0)
              e[m] = e1[m];
            else
              e[m] = j[m];
      }
      var Q6 = arguments.length - 2;
      if (Q6 === 1)
        e.children = x;
      else if (Q6 > 1) {
        var q6 = Array(Q6);
        for (var R6 = 0;R6 < Q6; R6++)
          q6[R6] = arguments[R6 + 2];
        e.children = q6;
      }
      return d8(A.type, T0, O0, m0, P1, m1, e);
    }
    function f0(A) {
      return typeof A === "object" && A !== null && A.$$typeof === J;
    }
    var k1 = ".", h1 = ":";
    function V6(A) {
      var j = /[=:]/g, x = {
        "=": "=0",
        ":": "=2"
      }, m = A.replace(j, function(e) {
        return x[e];
      });
      return "$" + m;
    }
    var a1 = !1, l8 = /\/+/g;
    function W1(A) {
      return A.replace(l8, "$&/");
    }
    function y1(A, j) {
      if (typeof A === "object" && A !== null && A.key != null)
        return v1(A.key), V6("" + A.key);
      return j.toString(36);
    }
    function t1(A, j, x, m, e) {
      var T0 = typeof A;
      if (T0 === "undefined" || T0 === "boolean")
        A = null;
      var O0 = !1;
      if (A === null)
        O0 = !0;
      else
        switch (T0) {
          case "string":
          case "number":
            O0 = !0;
            break;
          case "object":
            switch (A.$$typeof) {
              case J:
              case Y:
                O0 = !0;
            }
        }
      if (O0) {
        var m0 = A, P1 = e(m0), m1 = m === "" ? k1 + y1(m0, 0) : m;
        if (i1(P1)) {
          var e1 = "";
          if (m1 != null)
            e1 = W1(m1) + "/";
          t1(P1, j, e1, "", function(N7) {
            return N7;
          });
        } else if (P1 != null) {
          if (f0(P1)) {
            if (P1.key && (!m0 || m0.key !== P1.key))
              v1(P1.key);
            P1 = Q0(P1, x + (P1.key && (!m0 || m0.key !== P1.key) ? W1("" + P1.key) + "/" : "") + m1);
          }
          j.push(P1);
        }
        return 1;
      }
      var Q6, q6, R6 = 0, S1 = m === "" ? k1 : m + h1;
      if (i1(A))
        for (var lJ = 0;lJ < A.length; lJ++)
          Q6 = A[lJ], q6 = S1 + y1(Q6, lJ), R6 += t1(Q6, j, x, q6, e);
      else {
        var QY = F0(A);
        if (typeof QY === "function") {
          var mq = A;
          if (QY === mq.entries) {
            if (!a1)
              Y1("Using Maps as children is not supported. Use an array of keyed ReactElements instead.");
            a1 = !0;
          }
          var z7 = QY.call(mq), aX, bq = 0;
          while (!(aX = z7.next()).done)
            Q6 = aX.value, q6 = S1 + y1(Q6, bq++), R6 += t1(Q6, j, x, q6, e);
        } else if (T0 === "object") {
          var uq = String(A);
          throw new Error("Objects are not valid as a React child (found: " + (uq === "[object Object]" ? "object with keys {" + Object.keys(A).join(", ") + "}" : uq) + "). If you meant to render a collection of children, use an array instead.");
        }
      }
      return R6;
    }
    function X6(A, j, x) {
      if (A == null)
        return A;
      var m = [], e = 0;
      return t1(A, m, "", "", function(T0) {
        return j.call(x, T0, e++);
      }), m;
    }
    function L6(A) {
      var j = 0;
      return X6(A, function() {
        j++;
      }), j;
    }
    function n8(A, j, x) {
      X6(A, function() {
        j.apply(this, arguments);
      }, x);
    }
    function K8(A) {
      return X6(A, function(j) {
        return j;
      }) || [];
    }
    function H8(A) {
      if (!f0(A))
        throw new Error("React.Children.only expected to receive a single React element child.");
      return A;
    }
    function j8(A) {
      var j = {
        $$typeof: F,
        _currentValue: A,
        _currentValue2: A,
        _threadCount: 0,
        Provider: null,
        Consumer: null,
        _defaultValue: null,
        _globalName: null
      };
      j.Provider = {
        $$typeof: N,
        _context: j
      };
      var x = !1, m = !1, e = !1;
      {
        var T0 = {
          $$typeof: F,
          _context: j
        };
        Object.defineProperties(T0, {
          Provider: {
            get: function() {
              if (!m)
                m = !0, N0("Rendering <Context.Consumer.Provider> is not supported and will be removed in a future major release. Did you mean to render <Context.Provider> instead?");
              return j.Provider;
            },
            set: function(O0) {
              j.Provider = O0;
            }
          },
          _currentValue: {
            get: function() {
              return j._currentValue;
            },
            set: function(O0) {
              j._currentValue = O0;
            }
          },
          _currentValue2: {
            get: function() {
              return j._currentValue2;
            },
            set: function(O0) {
              j._currentValue2 = O0;
            }
          },
          _threadCount: {
            get: function() {
              return j._threadCount;
            },
            set: function(O0) {
              j._threadCount = O0;
            }
          },
          Consumer: {
            get: function() {
              if (!x)
                x = !0, N0("Rendering <Context.Consumer.Consumer> is not supported and will be removed in a future major release. Did you mean to render <Context.Consumer> instead?");
              return j.Consumer;
            }
          },
          displayName: {
            get: function() {
              return j.displayName;
            },
            set: function(O0) {
              if (!e)
                Y1("Setting `displayName` on Context.Consumer has no effect. You should set it directly on the context with Context.displayName = '%s'.", O0), e = !0;
            }
          }
        }), j.Consumer = T0;
      }
      return j._currentRenderer = null, j._currentRenderer2 = null, j;
    }
    var G8 = -1, y6 = 0, BQ = 1, s8 = 2;
    function o8(A) {
      if (A._status === G8) {
        var j = A._result, x = j();
        if (x.then(function(T0) {
          if (A._status === y6 || A._status === G8) {
            var O0 = A;
            O0._status = BQ, O0._result = T0;
          }
        }, function(T0) {
          if (A._status === y6 || A._status === G8) {
            var O0 = A;
            O0._status = s8, O0._result = T0;
          }
        }), A._status === G8) {
          var m = A;
          m._status = y6, m._result = x;
        }
      }
      if (A._status === BQ) {
        var e = A._result;
        if (e === void 0)
          N0(`lazy: Expected the result of a dynamic import() call. Instead received: %s

Your code should look like: 
  const MyComponent = lazy(() => import('./MyComponent'))

Did you accidentally put curly braces around the import?`, e);
        if (!("default" in e))
          N0(`lazy: Expected the result of a dynamic import() call. Instead received: %s

Your code should look like: 
  const MyComponent = lazy(() => import('./MyComponent'))`, e);
        return e.default;
      } else
        throw A._result;
    }
    function KQ(A) {
      var j = {
        _status: G8,
        _result: A
      }, x = {
        $$typeof: V,
        _payload: j,
        _init: o8
      };
      {
        var m, e;
        Object.defineProperties(x, {
          defaultProps: {
            configurable: !0,
            get: function() {
              return m;
            },
            set: function(T0) {
              N0("React.lazy(...): It is not supported to assign `defaultProps` to a lazy component import. Either specify them where the component is defined, or create a wrapping component around it."), m = T0, Object.defineProperty(x, "defaultProps", {
                enumerable: !0
              });
            }
          },
          propTypes: {
            configurable: !0,
            get: function() {
              return e;
            },
            set: function(T0) {
              N0("React.lazy(...): It is not supported to assign `propTypes` to a lazy component import. Either specify them where the component is defined, or create a wrapping component around it."), e = T0, Object.defineProperty(x, "propTypes", {
                enumerable: !0
              });
            }
          }
        });
      }
      return x;
    }
    function PX(A) {
      {
        if (A != null && A.$$typeof === R)
          N0("forwardRef requires a render function but received a `memo` component. Instead of forwardRef(memo(...)), use memo(forwardRef(...)).");
        else if (typeof A !== "function")
          N0("forwardRef requires a render function but was given %s.", A === null ? "null" : typeof A);
        else if (A.length !== 0 && A.length !== 2)
          N0("forwardRef render functions accept exactly two parameters: props and ref. %s", A.length === 1 ? "Did you forget to use the ref parameter?" : "Any additional parameter will be undefined.");
        if (A != null) {
          if (A.defaultProps != null || A.propTypes != null)
            N0("forwardRef render functions do not support propTypes or defaultProps. Did you accidentally pass a React component?");
        }
      }
      var j = {
        $$typeof: L,
        render: A
      };
      {
        var x;
        Object.defineProperty(j, "displayName", {
          enumerable: !1,
          configurable: !0,
          get: function() {
            return x;
          },
          set: function(m) {
            if (x = m, !A.name && !A.displayName)
              A.displayName = m;
          }
        });
      }
      return j;
    }
    var pQ = Symbol.for("react.module.reference");
    function HQ(A) {
      if (typeof A === "string" || typeof A === "function")
        return !0;
      if (A === W || A === z || A0 || A === K || A === w || A === D || Y0 || A === g || I0 || p || o)
        return !0;
      if (typeof A === "object" && A !== null) {
        if (A.$$typeof === V || A.$$typeof === R || A.$$typeof === N || A.$$typeof === F || A.$$typeof === L || A.$$typeof === pQ || A.getModuleId !== void 0)
          return !0;
      }
      return !1;
    }
    function fZ(A, j) {
      if (!HQ(A))
        N0("memo: The first argument must be a component. Instead received: %s", A === null ? "null" : typeof A);
      var x = {
        $$typeof: R,
        type: A,
        compare: j === void 0 ? null : j
      };
      {
        var m;
        Object.defineProperty(x, "displayName", {
          enumerable: !1,
          configurable: !0,
          get: function() {
            return m;
          },
          set: function(e) {
            if (m = e, !A.name && !A.displayName)
              A.displayName = e;
          }
        });
      }
      return x;
    }
    function V1() {
      var A = r.current;
      if (A === null)
        N0(`Invalid hook call. Hooks can only be called inside of the body of a function component. This could happen for one of the following reasons:
1. You might have mismatching versions of React and the renderer (such as React DOM)
2. You might be breaking the Rules of Hooks
3. You might have more than one copy of React in the same app
See https://reactjs.org/link/invalid-hook-call for tips about how to debug and fix this problem.`);
      return A;
    }
    function V4(A) {
      var j = V1();
      if (A._context !== void 0) {
        var x = A._context;
        if (x.Consumer === A)
          N0("Calling useContext(Context.Consumer) is not supported, may cause bugs, and will be removed in a future major release. Did you mean to call useContext(Context) instead?");
        else if (x.Provider === A)
          N0("Calling useContext(Context.Provider) is not supported. Did you mean to call useContext(Context) instead?");
      }
      return j.useContext(A);
    }
    function S4(A) {
      var j = V1();
      return j.useState(A);
    }
    function nX(A, j, x) {
      var m = V1();
      return m.useReducer(A, j, x);
    }
    function n6(A) {
      var j = V1();
      return j.useRef(A);
    }
    function xq(A, j) {
      var x = V1();
      return x.useEffect(A, j);
    }
    function vq(A, j) {
      var x = V1();
      return x.useInsertionEffect(A, j);
    }
    function s$(A, j) {
      var x = V1();
      return x.useLayoutEffect(A, j);
    }
    function hq(A, j) {
      var x = V1();
      return x.useCallback(A, j);
    }
    function yq(A, j) {
      var x = V1();
      return x.useMemo(A, j);
    }
    function fq(A, j, x) {
      var m = V1();
      return m.useImperativeHandle(A, j, x);
    }
    function bJ(A, j) {
      {
        var x = V1();
        return x.useDebugValue(A, j);
      }
    }
    function o$() {
      var A = V1();
      return A.useTransition();
    }
    function mZ(A) {
      var j = V1();
      return j.useDeferredValue(A);
    }
    function K1() {
      var A = V1();
      return A.useId();
    }
    function AX(A, j, x) {
      var m = V1();
      return m.useSyncExternalStore(A, j, x);
    }
    var LX = 0, I4, _4, T4, uJ, g4, x4, cJ;
    function a$() {}
    a$.__reactDisabledLog = !0;
    function r$() {
      {
        if (LX === 0) {
          I4 = console.log, _4 = console.info, T4 = console.warn, uJ = console.error, g4 = console.group, x4 = console.groupCollapsed, cJ = console.groupEnd;
          var A = {
            configurable: !0,
            enumerable: !0,
            value: a$,
            writable: !0
          };
          Object.defineProperties(console, {
            info: A,
            log: A,
            warn: A,
            error: A,
            group: A,
            groupCollapsed: A,
            groupEnd: A
          });
        }
        LX++;
      }
    }
    function pJ() {
      {
        if (LX--, LX === 0) {
          var A = {
            configurable: !0,
            enumerable: !0,
            writable: !0
          };
          Object.defineProperties(console, {
            log: s1({}, A, {
              value: I4
            }),
            info: s1({}, A, {
              value: _4
            }),
            warn: s1({}, A, {
              value: T4
            }),
            error: s1({}, A, {
              value: uJ
            }),
            group: s1({}, A, {
              value: g4
            }),
            groupCollapsed: s1({}, A, {
              value: x4
            }),
            groupEnd: s1({}, A, {
              value: cJ
            })
          });
        }
        if (LX < 0)
          N0("disabledDepth fell below zero. This is a bug in React. Please file an issue.");
      }
    }
    var sX = P0.ReactCurrentDispatcher, CQ;
    function OX(A, j, x) {
      {
        if (CQ === void 0)
          try {
            throw Error();
          } catch (e) {
            var m = e.stack.trim().match(/\n( *(at )?)/);
            CQ = m && m[1] || "";
          }
        return `
` + CQ + A;
      }
    }
    var wX = !1, v4;
    {
      var M = typeof WeakMap === "function" ? WeakMap : Map;
      v4 = new M;
    }
    function S(A, j) {
      if (!A || wX)
        return "";
      {
        var x = v4.get(A);
        if (x !== void 0)
          return x;
      }
      var m;
      wX = !0;
      var e = Error.prepareStackTrace;
      Error.prepareStackTrace = void 0;
      var T0;
      T0 = sX.current, sX.current = null, r$();
      try {
        if (j) {
          var O0 = function() {
            throw Error();
          };
          if (Object.defineProperty(O0.prototype, "props", {
            set: function() {
              throw Error();
            }
          }), typeof Reflect === "object" && Reflect.construct) {
            try {
              Reflect.construct(O0, []);
            } catch (S1) {
              m = S1;
            }
            Reflect.construct(A, [], O0);
          } else {
            try {
              O0.call();
            } catch (S1) {
              m = S1;
            }
            A.call(O0.prototype);
          }
        } else {
          try {
            throw Error();
          } catch (S1) {
            m = S1;
          }
          A();
        }
      } catch (S1) {
        if (S1 && m && typeof S1.stack === "string") {
          var m0 = S1.stack.split(`
`), P1 = m.stack.split(`
`), m1 = m0.length - 1, e1 = P1.length - 1;
          while (m1 >= 1 && e1 >= 0 && m0[m1] !== P1[e1])
            e1--;
          for (;m1 >= 1 && e1 >= 0; m1--, e1--)
            if (m0[m1] !== P1[e1]) {
              if (m1 !== 1 || e1 !== 1)
                do
                  if (m1--, e1--, e1 < 0 || m0[m1] !== P1[e1]) {
                    var Q6 = `
` + m0[m1].replace(" at new ", " at ");
                    if (A.displayName && Q6.includes("<anonymous>"))
                      Q6 = Q6.replace("<anonymous>", A.displayName);
                    if (typeof A === "function")
                      v4.set(A, Q6);
                    return Q6;
                  }
                while (m1 >= 1 && e1 >= 0);
              break;
            }
        }
      } finally {
        wX = !1, sX.current = T0, pJ(), Error.prepareStackTrace = e;
      }
      var q6 = A ? A.displayName || A.name : "", R6 = q6 ? OX(q6) : "";
      if (typeof A === "function")
        v4.set(A, R6);
      return R6;
    }
    function y(A, j, x) {
      return S(A, !1);
    }
    function d(A) {
      var j = A.prototype;
      return !!(j && j.isReactComponent);
    }
    function K0(A, j, x) {
      if (A == null)
        return "";
      if (typeof A === "function")
        return S(A, d(A));
      if (typeof A === "string")
        return OX(A);
      switch (A) {
        case w:
          return OX("Suspense");
        case D:
          return OX("SuspenseList");
      }
      if (typeof A === "object")
        switch (A.$$typeof) {
          case L:
            return y(A.render);
          case R:
            return K0(A.type, j, x);
          case V: {
            var m = A, e = m._payload, T0 = m._init;
            try {
              return K0(T0(e), j, x);
            } catch (O0) {}
          }
        }
      return "";
    }
    var H1 = {}, _0 = P0.ReactDebugCurrentFrame;
    function d0(A) {
      if (A) {
        var j = A._owner, x = K0(A.type, A._source, j ? j.type : null);
        _0.setExtraStackFrame(x);
      } else
        _0.setExtraStackFrame(null);
    }
    function O6(A, j, x, m, e) {
      {
        var T0 = Function.call.bind(k8);
        for (var O0 in A)
          if (T0(A, O0)) {
            var m0 = void 0;
            try {
              if (typeof A[O0] !== "function") {
                var P1 = Error((m || "React class") + ": " + x + " type `" + O0 + "` is invalid; it must be a function, usually from the `prop-types` package, but received `" + typeof A[O0] + "`.This often happens because of typos such as `PropTypes.function` instead of `PropTypes.func`.");
                throw P1.name = "Invariant Violation", P1;
              }
              m0 = A[O0](j, O0, m, x, null, "SECRET_DO_NOT_PASS_THIS_OR_YOU_WILL_BE_FIRED");
            } catch (m1) {
              m0 = m1;
            }
            if (m0 && !(m0 instanceof Error))
              d0(e), N0("%s: type specification of %s `%s` is invalid; the type checker function must return `null` or an `Error` but returned a %s. You may have forgotten to pass an argument to the type checker creator (arrayOf, instanceOf, objectOf, oneOf, oneOfType, and shape all require an argument).", m || "React class", x, O0, typeof m0), d0(null);
            if (m0 instanceof Error && !(m0.message in H1))
              H1[m0.message] = !0, d0(e), N0("Failed %s type: %s", x, m0.message), d0(null);
          }
      }
    }
    function h0(A) {
      if (A) {
        var j = A._owner, x = K0(A.type, A._source, j ? j.type : null);
        c0(x);
      } else
        c0(null);
    }
    var B8 = !1;
    function s6() {
      if (t.current) {
        var A = p6(t.current.type);
        if (A)
          return `

Check the render method of \`` + A + "`.";
      }
      return "";
    }
    function V0(A) {
      if (A !== void 0) {
        var j = A.fileName.replace(/^.*[\\\/]/, ""), x = A.lineNumber;
        return `

Check your code at ` + j + ":" + x + ".";
      }
      return "";
    }
    function GQ(A) {
      if (A !== null && A !== void 0)
        return V0(A.__source);
      return "";
    }
    var z8 = {};
    function MX(A) {
      var j = s6();
      if (!j) {
        var x = typeof A === "string" ? A : A.displayName || A.name;
        if (x)
          j = `

Check the top-level render call using <` + x + ">.";
      }
      return j;
    }
    function bZ(A, j) {
      if (!A._store || A._store.validated || A.key != null)
        return;
      A._store.validated = !0;
      var x = MX(j);
      if (z8[x])
        return;
      z8[x] = !0;
      var m = "";
      if (A && A._owner && A._owner !== t.current)
        m = " It was passed a child from " + p6(A._owner.type) + ".";
      h0(A), N0('Each child in a list should have a unique "key" prop.%s%s See https://reactjs.org/link/warning-keys for more information.', x, m), h0(null);
    }
    function AK(A, j) {
      if (typeof A !== "object")
        return;
      if (i1(A))
        for (var x = 0;x < A.length; x++) {
          var m = A[x];
          if (f0(m))
            bZ(m, j);
        }
      else if (f0(A)) {
        if (A._store)
          A._store.validated = !0;
      } else if (A) {
        var e = F0(A);
        if (typeof e === "function") {
          if (e !== A.entries) {
            var T0 = e.call(A), O0;
            while (!(O0 = T0.next()).done)
              if (f0(O0.value))
                bZ(O0.value, j);
          }
        }
      }
    }
    function N8(A) {
      {
        var j = A.type;
        if (j === null || j === void 0 || typeof j === "string")
          return;
        var x;
        if (typeof j === "function")
          x = j.propTypes;
        else if (typeof j === "object" && (j.$$typeof === L || j.$$typeof === R))
          x = j.propTypes;
        else
          return;
        if (x) {
          var m = p6(j);
          O6(x, A.props, "prop", m, A);
        } else if (j.PropTypes !== void 0 && !B8) {
          B8 = !0;
          var e = p6(j);
          N0("Component %s declared `PropTypes` instead of `propTypes`. Did you misspell the property assignment?", e || "Unknown");
        }
        if (typeof j.getDefaultProps === "function" && !j.getDefaultProps.isReactClassApproved)
          N0("getDefaultProps is only used on classic React.createClass definitions. Use a static property named `defaultProps` instead.");
      }
    }
    function w6(A) {
      {
        var j = Object.keys(A.props);
        for (var x = 0;x < j.length; x++) {
          var m = j[x];
          if (m !== "children" && m !== "key") {
            h0(A), N0("Invalid prop `%s` supplied to `React.Fragment`. React.Fragment can only have `key` and `children` props.", m), h0(null);
            break;
          }
        }
        if (A.ref !== null)
          h0(A), N0("Invalid attribute `ref` supplied to `React.Fragment`."), h0(null);
      }
    }
    function LK(A, j, x) {
      var m = HQ(A);
      if (!m) {
        var e = "";
        if (A === void 0 || typeof A === "object" && A !== null && Object.keys(A).length === 0)
          e += " You likely forgot to export your component from the file it's defined in, or you might have mixed up default and named imports.";
        var T0 = GQ(j);
        if (T0)
          e += T0;
        else
          e += s6();
        var O0;
        if (A === null)
          O0 = "null";
        else if (i1(A))
          O0 = "array";
        else if (A !== void 0 && A.$$typeof === J)
          O0 = "<" + (p6(A.type) || "Unknown") + " />", e = " Did you accidentally export a JSX literal instead of a component?";
        else
          O0 = typeof A;
        N0("React.createElement: type is invalid -- expected a string (for built-in components) or a class/function (for composite components) but got: %s.%s", O0, e);
      }
      var m0 = jQ.apply(this, arguments);
      if (m0 == null)
        return m0;
      if (m)
        for (var P1 = 2;P1 < arguments.length; P1++)
          AK(arguments[P1], A);
      if (A === W)
        w6(m0);
      else
        N8(m0);
      return m0;
    }
    var dQ = !1;
    function VQ(A) {
      var j = LK.bind(null, A);
      j.type = A;
      {
        if (!dQ)
          dQ = !0, Y1("React.createFactory() is deprecated and will be removed in a future major release. Consider using JSX or use React.createElement() directly instead.");
        Object.defineProperty(j, "type", {
          enumerable: !1,
          get: function() {
            return Y1("Factory.type is deprecated. Access the class directly before passing it to createFactory."), Object.defineProperty(this, "type", {
              value: A
            }), A;
          }
        });
      }
      return j;
    }
    function DX(A, j, x) {
      var m = D0.apply(this, arguments);
      for (var e = 2;e < arguments.length; e++)
        AK(arguments[e], m.type);
      return N8(m), m;
    }
    function G7(A, j) {
      var x = J0.transition;
      J0.transition = {};
      var m = J0.transition;
      J0.transition._updatedFibers = /* @__PURE__ */ new Set;
      try {
        A();
      } finally {
        if (J0.transition = x, x === null && m._updatedFibers) {
          var e = m._updatedFibers.size;
          if (e > 10)
            Y1("Detected a large number of updates inside startTransition. If this is due to a subscription please re-write it to use React provided hooks. Otherwise concurrent mode guarantees are off the table.");
          m._updatedFibers.clear();
        }
      }
    }
    var i$ = !1, dJ = null;
    function OK(A) {
      if (dJ === null)
        try {
          var j = ("require" + Math.random()).slice(0, 7), x = V5 && V5[j];
          dJ = x.call(V5, "timers").setImmediate;
        } catch (m) {
          dJ = function(e) {
            if (i$ === !1) {
              if (i$ = !0, typeof MessageChannel === "undefined")
                N0("This browser does not have a MessageChannel implementation, so enqueuing tasks via await act(async () => ...) will fail. Please file an issue at https://github.com/facebook/react/issues if you encounter this warning.");
            }
            var T0 = new MessageChannel;
            T0.port1.onmessage = e, T0.port2.postMessage(void 0);
          };
        }
      return dJ(A);
    }
    var h4 = 0, wK = !1;
    function MK(A) {
      {
        var j = h4;
        if (h4++, l.current === null)
          l.current = [];
        var x = l.isBatchingLegacy, m;
        try {
          if (l.isBatchingLegacy = !0, m = A(), !x && l.didScheduleLegacyUpdate) {
            var e = l.current;
            if (e !== null)
              l.didScheduleLegacyUpdate = !1, e$(e);
          }
        } catch (q6) {
          throw oX(j), q6;
        } finally {
          l.isBatchingLegacy = x;
        }
        if (m !== null && typeof m === "object" && typeof m.then === "function") {
          var T0 = m, O0 = !1, m0 = {
            then: function(q6, R6) {
              O0 = !0, T0.then(function(S1) {
                if (oX(j), h4 === 0)
                  t$(S1, q6, R6);
                else
                  q6(S1);
              }, function(S1) {
                oX(j), R6(S1);
              });
            }
          };
          if (!wK && typeof Promise !== "undefined")
            Promise.resolve().then(function() {}).then(function() {
              if (!O0)
                wK = !0, N0("You called act(async () => ...) without await. This could lead to unexpected testing behaviour, interleaving multiple act calls and mixing their scopes. You should - await act(async () => ...);");
            });
          return m0;
        } else {
          var P1 = m;
          if (oX(j), h4 === 0) {
            var m1 = l.current;
            if (m1 !== null)
              e$(m1), l.current = null;
            var e1 = {
              then: function(q6, R6) {
                if (l.current === null)
                  l.current = [], t$(P1, q6, R6);
                else
                  q6(P1);
              }
            };
            return e1;
          } else {
            var Q6 = {
              then: function(q6, R6) {
                q6(P1);
              }
            };
            return Q6;
          }
        }
      }
    }
    function oX(A) {
      {
        if (A !== h4 - 1)
          N0("You seem to have overlapping act() calls, this is not supported. Be sure to await previous act() calls before making a new one. ");
        h4 = A;
      }
    }
    function t$(A, j, x) {
      {
        var m = l.current;
        if (m !== null)
          try {
            e$(m), OK(function() {
              if (m.length === 0)
                l.current = null, j(A);
              else
                t$(A, j, x);
            });
          } catch (e) {
            x(e);
          }
        else
          j(A);
      }
    }
    var y4 = !1;
    function e$(A) {
      if (!y4) {
        y4 = !0;
        var j = 0;
        try {
          for (;j < A.length; j++) {
            var x = A[j];
            do
              x = x(!0);
            while (x !== null);
          }
          A.length = 0;
        } catch (m) {
          throw A = A.slice(j + 1), m;
        } finally {
          y4 = !1;
        }
      }
    }
    var DK = LK, kK = DX, RK = VQ, jK = {
      map: X6,
      forEach: n8,
      count: L6,
      toArray: K8,
      only: H8
    };
    if (wx.Children = jK, wx.Component = U1, wx.Fragment = W, wx.Profiler = z, wx.PureComponent = f1, wx.StrictMode = K, wx.Suspense = w, wx.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED = P0, wx.act = MK, wx.cloneElement = kK, wx.createContext = j8, wx.createElement = DK, wx.createFactory = RK, wx.createRef = x1, wx.forwardRef = PX, wx.isValidElement = f0, wx.lazy = KQ, wx.memo = fZ, wx.startTransition = G7, wx.unstable_act = MK, wx.useCallback = hq, wx.useContext = V4, wx.useDebugValue = bJ, wx.useDeferredValue = mZ, wx.useEffect = xq, wx.useId = K1, wx.useImperativeHandle = fq, wx.useInsertionEffect = vq, wx.useLayoutEffect = s$, wx.useMemo = yq, wx.useReducer = nX, wx.useRef = n6, wx.useState = S4, wx.useSyncExternalStore = AX, wx.useTransition = o$, wx.version = Q, typeof __REACT_DEVTOOLS_GLOBAL_HOOK__ !== "undefined" && typeof __REACT_DEVTOOLS_GLOBAL_HOOK__.registerInternalModuleStop === "function")
      __REACT_DEVTOOLS_GLOBAL_HOOK__.registerInternalModuleStop(new Error);
  })();
});

// node_modules/scheduler/cjs/scheduler.development.js
var Rw = $6((Mx) => {
  (function() {
    if (typeof __REACT_DEVTOOLS_GLOBAL_HOOK__ !== "undefined" && typeof __REACT_DEVTOOLS_GLOBAL_HOOK__.registerInternalModuleStart === "function")
      __REACT_DEVTOOLS_GLOBAL_HOOK__.registerInternalModuleStart(new Error);
    var Q = !1, J = !1, Y = 5;
    function W(Q0, D0) {
      var f0 = Q0.length;
      Q0.push(D0), N(Q0, D0, f0);
    }
    function K(Q0) {
      return Q0.length === 0 ? null : Q0[0];
    }
    function z(Q0) {
      if (Q0.length === 0)
        return null;
      var D0 = Q0[0], f0 = Q0.pop();
      if (f0 !== D0)
        Q0[0] = f0, F(Q0, f0, 0);
      return D0;
    }
    function N(Q0, D0, f0) {
      var k1 = f0;
      while (k1 > 0) {
        var h1 = k1 - 1 >>> 1, V6 = Q0[h1];
        if (L(V6, D0) > 0)
          Q0[h1] = D0, Q0[k1] = V6, k1 = h1;
        else
          return;
      }
    }
    function F(Q0, D0, f0) {
      var k1 = f0, h1 = Q0.length, V6 = h1 >>> 1;
      while (k1 < V6) {
        var a1 = (k1 + 1) * 2 - 1, l8 = Q0[a1], W1 = a1 + 1, y1 = Q0[W1];
        if (L(l8, D0) < 0)
          if (W1 < h1 && L(y1, l8) < 0)
            Q0[k1] = y1, Q0[W1] = D0, k1 = W1;
          else
            Q0[k1] = l8, Q0[a1] = D0, k1 = a1;
        else if (W1 < h1 && L(y1, D0) < 0)
          Q0[k1] = y1, Q0[W1] = D0, k1 = W1;
        else
          return;
      }
    }
    function L(Q0, D0) {
      var f0 = Q0.sortIndex - D0.sortIndex;
      return f0 !== 0 ? f0 : Q0.id - D0.id;
    }
    var w = 1, D = 2, R = 3, V = 4, g = 5;
    function s(Q0, D0) {}
    var i = typeof performance === "object" && typeof performance.now === "function";
    if (i) {
      var F0 = performance;
      Mx.unstable_now = function() {
        return F0.now();
      };
    } else {
      var r = Date, J0 = r.now();
      Mx.unstable_now = function() {
        return r.now() - J0;
      };
    }
    var l = 1073741823, t = -1, $0 = 250, M0 = 5000, c0 = 1e4, I0 = l, p = [], o = [], Y0 = 1, A0 = null, P0 = R, Y1 = !1, N0 = !1, W0 = !1, v0 = typeof setTimeout === "function" ? setTimeout : null, n1 = typeof clearTimeout === "function" ? clearTimeout : null, g1 = typeof setImmediate !== "undefined" ? setImmediate : null, s1 = typeof navigator !== "undefined" && navigator.scheduling !== void 0 && navigator.scheduling.isInputPending !== void 0 ? navigator.scheduling.isInputPending.bind(navigator.scheduling) : null;
    function _1(Q0) {
      var D0 = K(o);
      while (D0 !== null) {
        if (D0.callback === null)
          z(o);
        else if (D0.startTime <= Q0)
          z(o), D0.sortIndex = D0.expirationTime, W(p, D0);
        else
          return;
        D0 = K(o);
      }
    }
    function U1(Q0) {
      if (W0 = !1, _1(Q0), !N0)
        if (K(p) !== null)
          N0 = !0, WQ(x0);
        else {
          var D0 = K(o);
          if (D0 !== null)
            l6(U1, D0.startTime - Q0);
        }
    }
    function x0(Q0, D0) {
      if (N0 = !1, W0)
        W0 = !1, p8();
      Y1 = !0;
      var f0 = P0;
      try {
        if (J)
          try {
            return N6(Q0, D0);
          } catch (h1) {
            if (A0 !== null) {
              var k1 = Mx.unstable_now();
              s(A0, k1), A0.isQueued = !1;
            }
            throw h1;
          }
        else
          return N6(Q0, D0);
      } finally {
        A0 = null, P0 = f0, Y1 = !1;
      }
    }
    function N6(Q0, D0) {
      var f0 = D0;
      _1(f0), A0 = K(p);
      while (A0 !== null && !Q) {
        if (A0.expirationTime > f0 && (!Q0 || k8()))
          break;
        var k1 = A0.callback;
        if (typeof k1 === "function") {
          A0.callback = null, P0 = A0.priorityLevel;
          var h1 = A0.expirationTime <= f0, V6 = k1(h1);
          if (f0 = Mx.unstable_now(), typeof V6 === "function")
            A0.callback = V6;
          else if (A0 === K(p))
            z(p);
          _1(f0);
        } else
          z(p);
        A0 = K(p);
      }
      if (A0 !== null)
        return !0;
      else {
        var a1 = K(o);
        if (a1 !== null)
          l6(U1, a1.startTime - f0);
        return !1;
      }
    }
    function C6(Q0, D0) {
      switch (Q0) {
        case w:
        case D:
        case R:
        case V:
        case g:
          break;
        default:
          Q0 = R;
      }
      var f0 = P0;
      P0 = Q0;
      try {
        return D0();
      } finally {
        P0 = f0;
      }
    }
    function o1(Q0) {
      var D0;
      switch (P0) {
        case w:
        case D:
        case R:
          D0 = R;
          break;
        default:
          D0 = P0;
          break;
      }
      var f0 = P0;
      P0 = D0;
      try {
        return Q0();
      } finally {
        P0 = f0;
      }
    }
    function f1(Q0) {
      var D0 = P0;
      return function() {
        var f0 = P0;
        P0 = D0;
        try {
          return Q0.apply(this, arguments);
        } finally {
          P0 = f0;
        }
      };
    }
    function E6(Q0, D0, f0) {
      var k1 = Mx.unstable_now(), h1;
      if (typeof f0 === "object" && f0 !== null) {
        var V6 = f0.delay;
        if (typeof V6 === "number" && V6 > 0)
          h1 = k1 + V6;
        else
          h1 = k1;
      } else
        h1 = k1;
      var a1;
      switch (Q0) {
        case w:
          a1 = t;
          break;
        case D:
          a1 = $0;
          break;
        case g:
          a1 = I0;
          break;
        case V:
          a1 = c0;
          break;
        case R:
        default:
          a1 = M0;
          break;
      }
      var l8 = h1 + a1, W1 = {
        id: Y0++,
        callback: D0,
        priorityLevel: Q0,
        startTime: h1,
        expirationTime: l8,
        sortIndex: -1
      };
      if (h1 > k1) {
        if (W1.sortIndex = h1, W(o, W1), K(p) === null && W1 === K(o)) {
          if (W0)
            p8();
          else
            W0 = !0;
          l6(U1, h1 - k1);
        }
      } else if (W1.sortIndex = l8, W(p, W1), !N0 && !Y1)
        N0 = !0, WQ(x0);
      return W1;
    }
    function x1() {}
    function l0() {
      if (!N0 && !Y1)
        N0 = !0, WQ(x0);
    }
    function i1() {
      return K(p);
    }
    function Z0(Q0) {
      Q0.callback = null;
    }
    function F6() {
      return P0;
    }
    var C1 = !1, v1 = null, h6 = -1, c8 = Y, p6 = -1;
    function k8() {
      var Q0 = Mx.unstable_now() - p6;
      if (Q0 < c8)
        return !1;
      return !0;
    }
    function q8() {}
    function W8(Q0) {
      if (Q0 < 0 || Q0 > 125) {
        console.error("forceFrameRate takes a positive int between 0 and 125, forcing frame rates higher than 125 fps is not supported");
        return;
      }
      if (Q0 > 0)
        c8 = Math.floor(1000 / Q0);
      else
        c8 = Y;
    }
    var d6 = function() {
      if (v1 !== null) {
        var Q0 = Mx.unstable_now();
        p6 = Q0;
        var D0 = !0, f0 = !0;
        try {
          f0 = v1(D0, Q0);
        } finally {
          if (f0)
            A6();
          else
            C1 = !1, v1 = null;
        }
      } else
        C1 = !1;
    }, A6;
    if (typeof g1 === "function")
      A6 = function() {
        g1(d6);
      };
    else if (typeof MessageChannel !== "undefined") {
      var RQ = new MessageChannel, R8 = RQ.port2;
      RQ.port1.onmessage = d6, A6 = function() {
        R8.postMessage(null);
      };
    } else
      A6 = function() {
        v0(d6, 0);
      };
    function WQ(Q0) {
      if (v1 = Q0, !C1)
        C1 = !0, A6();
    }
    function l6(Q0, D0) {
      h6 = v0(function() {
        Q0(Mx.unstable_now());
      }, D0);
    }
    function p8() {
      n1(h6), h6 = -1;
    }
    var d8 = q8, jQ = null;
    if (Mx.unstable_IdlePriority = g, Mx.unstable_ImmediatePriority = w, Mx.unstable_LowPriority = V, Mx.unstable_NormalPriority = R, Mx.unstable_Profiling = jQ, Mx.unstable_UserBlockingPriority = D, Mx.unstable_cancelCallback = Z0, Mx.unstable_continueExecution = l0, Mx.unstable_forceFrameRate = W8, Mx.unstable_getCurrentPriorityLevel = F6, Mx.unstable_getFirstCallbackNode = i1, Mx.unstable_next = o1, Mx.unstable_pauseExecution = x1, Mx.unstable_requestPaint = d8, Mx.unstable_runWithPriority = C6, Mx.unstable_scheduleCallback = E6, Mx.unstable_shouldYield = k8, Mx.unstable_wrapCallback = f1, typeof __REACT_DEVTOOLS_GLOBAL_HOOK__ !== "undefined" && typeof __REACT_DEVTOOLS_GLOBAL_HOOK__.registerInternalModuleStop === "function")
      __REACT_DEVTOOLS_GLOBAL_HOOK__.registerInternalModuleStop(new Error);
  })();
});

// node_modules/react-dom/cjs/react-dom.development.js
var jw = $6((Dx) => {
  var A3 = D6(LQ(), 1), p1 = D6(Rw(), 1);
  (function() {
    if (typeof __REACT_DEVTOOLS_GLOBAL_HOOK__ !== "undefined" && typeof __REACT_DEVTOOLS_GLOBAL_HOOK__.registerInternalModuleStart === "function")
      __REACT_DEVTOOLS_GLOBAL_HOOK__.registerInternalModuleStart(new Error);
    var Q = A3.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED, J = !1;
    function Y(Z) {
      J = Z;
    }
    function W(Z) {
      if (!J) {
        for (var X = arguments.length, $ = new Array(X > 1 ? X - 1 : 0), q = 1;q < X; q++)
          $[q - 1] = arguments[q];
        z("warn", Z, $);
      }
    }
    function K(Z) {
      if (!J) {
        for (var X = arguments.length, $ = new Array(X > 1 ? X - 1 : 0), q = 1;q < X; q++)
          $[q - 1] = arguments[q];
        z("error", Z, $);
      }
    }
    function z(Z, X, $) {
      {
        var q = Q.ReactDebugCurrentFrame, H = q.getStackAddendum();
        if (H !== "")
          X += "%s", $ = $.concat([H]);
        var G = $.map(function(E) {
          return String(E);
        });
        G.unshift("Warning: " + X), Function.prototype.apply.call(console[Z], console, G);
      }
    }
    var N = 0, F = 1, L = 2, w = 3, D = 4, R = 5, V = 6, g = 7, s = 8, i = 9, F0 = 10, r = 11, J0 = 12, l = 13, t = 14, $0 = 15, M0 = 16, c0 = 17, I0 = 18, p = 19, o = 21, Y0 = 22, A0 = 23, P0 = 24, Y1 = 25, N0 = !0, W0 = !1, v0 = !1, n1 = !1, g1 = !1, s1 = !0, _1 = !1, U1 = !0, x0 = !0, N6 = !0, C6 = !0, o1 = /* @__PURE__ */ new Set, f1 = {}, E6 = {};
    function x1(Z, X) {
      l0(Z, X), l0(Z + "Capture", X);
    }
    function l0(Z, X) {
      if (f1[Z])
        K("EventRegistry: More than one plugin attempted to publish the same registration name, `%s`.", Z);
      f1[Z] = X;
      {
        var $ = Z.toLowerCase();
        if (E6[$] = Z, Z === "onDoubleClick")
          E6.ondblclick = Z;
      }
      for (var q = 0;q < X.length; q++)
        o1.add(X[q]);
    }
    var i1 = typeof window !== "undefined" && typeof window.document !== "undefined" && typeof window.document.createElement !== "undefined", Z0 = Object.prototype.hasOwnProperty;
    function F6(Z) {
      {
        var X = typeof Symbol === "function" && Symbol.toStringTag, $ = X && Z[Symbol.toStringTag] || Z.constructor.name || "Object";
        return $;
      }
    }
    function C1(Z) {
      try {
        return v1(Z), !1;
      } catch (X) {
        return !0;
      }
    }
    function v1(Z) {
      return "" + Z;
    }
    function h6(Z, X) {
      if (C1(Z))
        return K("The provided `%s` attribute is an unsupported type %s. This value must be coerced to a string before before using it here.", X, F6(Z)), v1(Z);
    }
    function c8(Z) {
      if (C1(Z))
        return K("The provided key is an unsupported type %s. This value must be coerced to a string before before using it here.", F6(Z)), v1(Z);
    }
    function p6(Z, X) {
      if (C1(Z))
        return K("The provided `%s` prop is an unsupported type %s. This value must be coerced to a string before before using it here.", X, F6(Z)), v1(Z);
    }
    function k8(Z, X) {
      if (C1(Z))
        return K("The provided `%s` CSS property is an unsupported type %s. This value must be coerced to a string before before using it here.", X, F6(Z)), v1(Z);
    }
    function q8(Z) {
      if (C1(Z))
        return K("The provided HTML markup uses a value of unsupported type %s. This value must be coerced to a string before before using it here.", F6(Z)), v1(Z);
    }
    function W8(Z) {
      if (C1(Z))
        return K("Form field values (value, checked, defaultValue, or defaultChecked props) must be strings, not %s. This value must be coerced to a string before before using it here.", F6(Z)), v1(Z);
    }
    var d6 = 0, A6 = 1, RQ = 2, R8 = 3, WQ = 4, l6 = 5, p8 = 6, d8 = ":A-Z_a-z\\u00C0-\\u00D6\\u00D8-\\u00F6\\u00F8-\\u02FF\\u0370-\\u037D\\u037F-\\u1FFF\\u200C-\\u200D\\u2070-\\u218F\\u2C00-\\u2FEF\\u3001-\\uD7FF\\uF900-\\uFDCF\\uFDF0-\\uFFFD", jQ = d8 + "\\-.0-9\\u00B7\\u0300-\\u036F\\u203F-\\u2040", Q0 = new RegExp("^[" + d8 + "][" + jQ + "]*$"), D0 = {}, f0 = {};
    function k1(Z) {
      if (Z0.call(f0, Z))
        return !0;
      if (Z0.call(D0, Z))
        return !1;
      if (Q0.test(Z))
        return f0[Z] = !0, !0;
      return D0[Z] = !0, K("Invalid attribute name: `%s`", Z), !1;
    }
    function h1(Z, X, $) {
      if (X !== null)
        return X.type === d6;
      if ($)
        return !1;
      if (Z.length > 2 && (Z[0] === "o" || Z[0] === "O") && (Z[1] === "n" || Z[1] === "N"))
        return !0;
      return !1;
    }
    function V6(Z, X, $, q) {
      if ($ !== null && $.type === d6)
        return !1;
      switch (typeof X) {
        case "function":
        case "symbol":
          return !0;
        case "boolean": {
          if (q)
            return !1;
          if ($ !== null)
            return !$.acceptsBooleans;
          else {
            var H = Z.toLowerCase().slice(0, 5);
            return H !== "data-" && H !== "aria-";
          }
        }
        default:
          return !1;
      }
    }
    function a1(Z, X, $, q) {
      if (X === null || typeof X === "undefined")
        return !0;
      if (V6(Z, X, $, q))
        return !0;
      if (q)
        return !1;
      if ($ !== null)
        switch ($.type) {
          case R8:
            return !X;
          case WQ:
            return X === !1;
          case l6:
            return isNaN(X);
          case p8:
            return isNaN(X) || X < 1;
        }
      return !1;
    }
    function l8(Z) {
      return y1.hasOwnProperty(Z) ? y1[Z] : null;
    }
    function W1(Z, X, $, q, H, G, E) {
      this.acceptsBooleans = X === RQ || X === R8 || X === WQ, this.attributeName = q, this.attributeNamespace = H, this.mustUseProperty = $, this.propertyName = Z, this.type = X, this.sanitizeURL = G, this.removeEmptyString = E;
    }
    var y1 = {}, t1 = [
      "children",
      "dangerouslySetInnerHTML",
      "defaultValue",
      "defaultChecked",
      "innerHTML",
      "suppressContentEditableWarning",
      "suppressHydrationWarning",
      "style"
    ];
    t1.forEach(function(Z) {
      y1[Z] = new W1(Z, d6, !1, Z, null, !1, !1);
    }), [["acceptCharset", "accept-charset"], ["className", "class"], ["htmlFor", "for"], ["httpEquiv", "http-equiv"]].forEach(function(Z) {
      var X = Z[0], $ = Z[1];
      y1[X] = new W1(X, A6, !1, $, null, !1, !1);
    }), ["contentEditable", "draggable", "spellCheck", "value"].forEach(function(Z) {
      y1[Z] = new W1(Z, RQ, !1, Z.toLowerCase(), null, !1, !1);
    }), ["autoReverse", "externalResourcesRequired", "focusable", "preserveAlpha"].forEach(function(Z) {
      y1[Z] = new W1(Z, RQ, !1, Z, null, !1, !1);
    }), [
      "allowFullScreen",
      "async",
      "autoFocus",
      "autoPlay",
      "controls",
      "default",
      "defer",
      "disabled",
      "disablePictureInPicture",
      "disableRemotePlayback",
      "formNoValidate",
      "hidden",
      "loop",
      "noModule",
      "noValidate",
      "open",
      "playsInline",
      "readOnly",
      "required",
      "reversed",
      "scoped",
      "seamless",
      "itemScope"
    ].forEach(function(Z) {
      y1[Z] = new W1(Z, R8, !1, Z.toLowerCase(), null, !1, !1);
    }), [
      "checked",
      "multiple",
      "muted",
      "selected"
    ].forEach(function(Z) {
      y1[Z] = new W1(Z, R8, !0, Z, null, !1, !1);
    }), [
      "capture",
      "download"
    ].forEach(function(Z) {
      y1[Z] = new W1(Z, WQ, !1, Z, null, !1, !1);
    }), [
      "cols",
      "rows",
      "size",
      "span"
    ].forEach(function(Z) {
      y1[Z] = new W1(Z, p8, !1, Z, null, !1, !1);
    }), ["rowSpan", "start"].forEach(function(Z) {
      y1[Z] = new W1(Z, l6, !1, Z.toLowerCase(), null, !1, !1);
    });
    var X6 = /[\-\:]([a-z])/g, L6 = function(Z) {
      return Z[1].toUpperCase();
    };
    [
      "accent-height",
      "alignment-baseline",
      "arabic-form",
      "baseline-shift",
      "cap-height",
      "clip-path",
      "clip-rule",
      "color-interpolation",
      "color-interpolation-filters",
      "color-profile",
      "color-rendering",
      "dominant-baseline",
      "enable-background",
      "fill-opacity",
      "fill-rule",
      "flood-color",
      "flood-opacity",
      "font-family",
      "font-size",
      "font-size-adjust",
      "font-stretch",
      "font-style",
      "font-variant",
      "font-weight",
      "glyph-name",
      "glyph-orientation-horizontal",
      "glyph-orientation-vertical",
      "horiz-adv-x",
      "horiz-origin-x",
      "image-rendering",
      "letter-spacing",
      "lighting-color",
      "marker-end",
      "marker-mid",
      "marker-start",
      "overline-position",
      "overline-thickness",
      "paint-order",
      "panose-1",
      "pointer-events",
      "rendering-intent",
      "shape-rendering",
      "stop-color",
      "stop-opacity",
      "strikethrough-position",
      "strikethrough-thickness",
      "stroke-dasharray",
      "stroke-dashoffset",
      "stroke-linecap",
      "stroke-linejoin",
      "stroke-miterlimit",
      "stroke-opacity",
      "stroke-width",
      "text-anchor",
      "text-decoration",
      "text-rendering",
      "underline-position",
      "underline-thickness",
      "unicode-bidi",
      "unicode-range",
      "units-per-em",
      "v-alphabetic",
      "v-hanging",
      "v-ideographic",
      "v-mathematical",
      "vector-effect",
      "vert-adv-y",
      "vert-origin-x",
      "vert-origin-y",
      "word-spacing",
      "writing-mode",
      "xmlns:xlink",
      "x-height"
    ].forEach(function(Z) {
      var X = Z.replace(X6, L6);
      y1[X] = new W1(X, A6, !1, Z, null, !1, !1);
    }), [
      "xlink:actuate",
      "xlink:arcrole",
      "xlink:role",
      "xlink:show",
      "xlink:title",
      "xlink:type"
    ].forEach(function(Z) {
      var X = Z.replace(X6, L6);
      y1[X] = new W1(X, A6, !1, Z, "http://www.w3.org/1999/xlink", !1, !1);
    }), [
      "xml:base",
      "xml:lang",
      "xml:space"
    ].forEach(function(Z) {
      var X = Z.replace(X6, L6);
      y1[X] = new W1(X, A6, !1, Z, "http://www.w3.org/XML/1998/namespace", !1, !1);
    }), ["tabIndex", "crossOrigin"].forEach(function(Z) {
      y1[Z] = new W1(Z, A6, !1, Z.toLowerCase(), null, !1, !1);
    });
    var n8 = "xlinkHref";
    y1[n8] = new W1("xlinkHref", A6, !1, "xlink:href", "http://www.w3.org/1999/xlink", !0, !1), ["src", "href", "action", "formAction"].forEach(function(Z) {
      y1[Z] = new W1(Z, A6, !1, Z.toLowerCase(), null, !0, !0);
    });
    var K8 = /^[\u0000-\u001F ]*j[\r\n\t]*a[\r\n\t]*v[\r\n\t]*a[\r\n\t]*s[\r\n\t]*c[\r\n\t]*r[\r\n\t]*i[\r\n\t]*p[\r\n\t]*t[\r\n\t]*\:/i, H8 = !1;
    function j8(Z) {
      if (!H8 && K8.test(Z))
        H8 = !0, K("A future version of React will block javascript: URLs as a security precaution. Use event handlers instead if you can. If you need to generate unsafe HTML try using dangerouslySetInnerHTML instead. React was passed %s.", JSON.stringify(Z));
    }
    function G8(Z, X, $, q) {
      if (q.mustUseProperty) {
        var H = q.propertyName;
        return Z[H];
      } else {
        if (h6($, X), q.sanitizeURL)
          j8("" + $);
        var G = q.attributeName, E = null;
        if (q.type === WQ) {
          if (Z.hasAttribute(G)) {
            var U = Z.getAttribute(G);
            if (U === "")
              return !0;
            if (a1(X, $, q, !1))
              return U;
            if (U === "" + $)
              return $;
            return U;
          }
        } else if (Z.hasAttribute(G)) {
          if (a1(X, $, q, !1))
            return Z.getAttribute(G);
          if (q.type === R8)
            return $;
          E = Z.getAttribute(G);
        }
        if (a1(X, $, q, !1))
          return E === null ? $ : E;
        else if (E === "" + $)
          return $;
        else
          return E;
      }
    }
    function y6(Z, X, $, q) {
      {
        if (!k1(X))
          return;
        if (!Z.hasAttribute(X))
          return $ === void 0 ? void 0 : null;
        var H = Z.getAttribute(X);
        if (h6($, X), H === "" + $)
          return $;
        return H;
      }
    }
    function BQ(Z, X, $, q) {
      var H = l8(X);
      if (h1(X, H, q))
        return;
      if (a1(X, $, H, q))
        $ = null;
      if (q || H === null) {
        if (k1(X)) {
          var G = X;
          if ($ === null)
            Z.removeAttribute(G);
          else
            h6($, X), Z.setAttribute(G, "" + $);
        }
        return;
      }
      var E = H.mustUseProperty;
      if (E) {
        var U = H.propertyName;
        if ($ === null) {
          var P = H.type;
          Z[U] = P === R8 ? !1 : "";
        } else
          Z[U] = $;
        return;
      }
      var { attributeName: O, attributeNamespace: k } = H;
      if ($ === null)
        Z.removeAttribute(O);
      else {
        var C = H.type, B;
        if (C === R8 || C === WQ && $ === !0)
          B = "";
        else if (h6($, O), B = "" + $, H.sanitizeURL)
          j8(B.toString());
        if (k)
          Z.setAttributeNS(k, O, B);
        else
          Z.setAttribute(O, B);
      }
    }
    var s8 = Symbol.for("react.element"), o8 = Symbol.for("react.portal"), KQ = Symbol.for("react.fragment"), PX = Symbol.for("react.strict_mode"), pQ = Symbol.for("react.profiler"), HQ = Symbol.for("react.provider"), fZ = Symbol.for("react.context"), V1 = Symbol.for("react.forward_ref"), V4 = Symbol.for("react.suspense"), S4 = Symbol.for("react.suspense_list"), nX = Symbol.for("react.memo"), n6 = Symbol.for("react.lazy"), xq = Symbol.for("react.scope"), vq = Symbol.for("react.debug_trace_mode"), s$ = Symbol.for("react.offscreen"), hq = Symbol.for("react.legacy_hidden"), yq = Symbol.for("react.cache"), fq = Symbol.for("react.tracing_marker"), bJ = Symbol.iterator, o$ = "@@iterator";
    function mZ(Z) {
      if (Z === null || typeof Z !== "object")
        return null;
      var X = bJ && Z[bJ] || Z[o$];
      if (typeof X === "function")
        return X;
      return null;
    }
    var K1 = Object.assign, AX = 0, LX, I4, _4, T4, uJ, g4, x4;
    function cJ() {}
    cJ.__reactDisabledLog = !0;
    function a$() {
      {
        if (AX === 0) {
          LX = console.log, I4 = console.info, _4 = console.warn, T4 = console.error, uJ = console.group, g4 = console.groupCollapsed, x4 = console.groupEnd;
          var Z = {
            configurable: !0,
            enumerable: !0,
            value: cJ,
            writable: !0
          };
          Object.defineProperties(console, {
            info: Z,
            log: Z,
            warn: Z,
            error: Z,
            group: Z,
            groupCollapsed: Z,
            groupEnd: Z
          });
        }
        AX++;
      }
    }
    function r$() {
      {
        if (AX--, AX === 0) {
          var Z = {
            configurable: !0,
            enumerable: !0,
            writable: !0
          };
          Object.defineProperties(console, {
            log: K1({}, Z, {
              value: LX
            }),
            info: K1({}, Z, {
              value: I4
            }),
            warn: K1({}, Z, {
              value: _4
            }),
            error: K1({}, Z, {
              value: T4
            }),
            group: K1({}, Z, {
              value: uJ
            }),
            groupCollapsed: K1({}, Z, {
              value: g4
            }),
            groupEnd: K1({}, Z, {
              value: x4
            })
          });
        }
        if (AX < 0)
          K("disabledDepth fell below zero. This is a bug in React. Please file an issue.");
      }
    }
    var pJ = Q.ReactCurrentDispatcher, sX;
    function CQ(Z, X, $) {
      {
        if (sX === void 0)
          try {
            throw Error();
          } catch (H) {
            var q = H.stack.trim().match(/\n( *(at )?)/);
            sX = q && q[1] || "";
          }
        return `
` + sX + Z;
      }
    }
    var OX = !1, wX;
    {
      var v4 = typeof WeakMap === "function" ? WeakMap : Map;
      wX = new v4;
    }
    function M(Z, X) {
      if (!Z || OX)
        return "";
      {
        var $ = wX.get(Z);
        if ($ !== void 0)
          return $;
      }
      var q;
      OX = !0;
      var H = Error.prepareStackTrace;
      Error.prepareStackTrace = void 0;
      var G;
      G = pJ.current, pJ.current = null, a$();
      try {
        if (X) {
          var E = function() {
            throw Error();
          };
          if (Object.defineProperty(E.prototype, "props", {
            set: function() {
              throw Error();
            }
          }), typeof Reflect === "object" && Reflect.construct) {
            try {
              Reflect.construct(E, []);
            } catch (h) {
              q = h;
            }
            Reflect.construct(Z, [], E);
          } else {
            try {
              E.call();
            } catch (h) {
              q = h;
            }
            Z.call(E.prototype);
          }
        } else {
          try {
            throw Error();
          } catch (h) {
            q = h;
          }
          Z();
        }
      } catch (h) {
        if (h && q && typeof h.stack === "string") {
          var U = h.stack.split(`
`), P = q.stack.split(`
`), O = U.length - 1, k = P.length - 1;
          while (O >= 1 && k >= 0 && U[O] !== P[k])
            k--;
          for (;O >= 1 && k >= 0; O--, k--)
            if (U[O] !== P[k]) {
              if (O !== 1 || k !== 1)
                do
                  if (O--, k--, k < 0 || U[O] !== P[k]) {
                    var C = `
` + U[O].replace(" at new ", " at ");
                    if (Z.displayName && C.includes("<anonymous>"))
                      C = C.replace("<anonymous>", Z.displayName);
                    if (typeof Z === "function")
                      wX.set(Z, C);
                    return C;
                  }
                while (O >= 1 && k >= 0);
              break;
            }
        }
      } finally {
        OX = !1, pJ.current = G, r$(), Error.prepareStackTrace = H;
      }
      var B = Z ? Z.displayName || Z.name : "", v = B ? CQ(B) : "";
      if (typeof Z === "function")
        wX.set(Z, v);
      return v;
    }
    function S(Z, X, $) {
      return M(Z, !0);
    }
    function y(Z, X, $) {
      return M(Z, !1);
    }
    function d(Z) {
      var X = Z.prototype;
      return !!(X && X.isReactComponent);
    }
    function K0(Z, X, $) {
      if (Z == null)
        return "";
      if (typeof Z === "function")
        return M(Z, d(Z));
      if (typeof Z === "string")
        return CQ(Z);
      switch (Z) {
        case V4:
          return CQ("Suspense");
        case S4:
          return CQ("SuspenseList");
      }
      if (typeof Z === "object")
        switch (Z.$$typeof) {
          case V1:
            return y(Z.render);
          case nX:
            return K0(Z.type, X, $);
          case n6: {
            var q = Z, H = q._payload, G = q._init;
            try {
              return K0(G(H), X, $);
            } catch (E) {}
          }
        }
      return "";
    }
    function H1(Z) {
      var X = Z._debugOwner ? Z._debugOwner.type : null, $ = Z._debugSource;
      switch (Z.tag) {
        case R:
          return CQ(Z.type);
        case M0:
          return CQ("Lazy");
        case l:
          return CQ("Suspense");
        case p:
          return CQ("SuspenseList");
        case N:
        case L:
        case $0:
          return y(Z.type);
        case r:
          return y(Z.type.render);
        case F:
          return S(Z.type);
        default:
          return "";
      }
    }
    function _0(Z) {
      try {
        var X = "", $ = Z;
        do
          X += H1($), $ = $.return;
        while ($);
        return X;
      } catch (q) {
        return `
Error generating stack: ` + q.message + `
` + q.stack;
      }
    }
    function d0(Z, X, $) {
      var q = Z.displayName;
      if (q)
        return q;
      var H = X.displayName || X.name || "";
      return H !== "" ? $ + "(" + H + ")" : $;
    }
    function O6(Z) {
      return Z.displayName || "Context";
    }
    function h0(Z) {
      if (Z == null)
        return null;
      if (typeof Z.tag === "number")
        K("Received an unexpected object in getComponentNameFromType(). This is likely a bug in React. Please file an issue.");
      if (typeof Z === "function")
        return Z.displayName || Z.name || null;
      if (typeof Z === "string")
        return Z;
      switch (Z) {
        case KQ:
          return "Fragment";
        case o8:
          return "Portal";
        case pQ:
          return "Profiler";
        case PX:
          return "StrictMode";
        case V4:
          return "Suspense";
        case S4:
          return "SuspenseList";
      }
      if (typeof Z === "object")
        switch (Z.$$typeof) {
          case fZ:
            var X = Z;
            return O6(X) + ".Consumer";
          case HQ:
            var $ = Z;
            return O6($._context) + ".Provider";
          case V1:
            return d0(Z, Z.render, "ForwardRef");
          case nX:
            var q = Z.displayName || null;
            if (q !== null)
              return q;
            return h0(Z.type) || "Memo";
          case n6: {
            var H = Z, G = H._payload, E = H._init;
            try {
              return h0(E(G));
            } catch (U) {
              return null;
            }
          }
        }
      return null;
    }
    function B8(Z, X, $) {
      var q = X.displayName || X.name || "";
      return Z.displayName || (q !== "" ? $ + "(" + q + ")" : $);
    }
    function s6(Z) {
      return Z.displayName || "Context";
    }
    function V0(Z) {
      var { tag: X, type: $ } = Z;
      switch (X) {
        case P0:
          return "Cache";
        case i:
          var q = $;
          return s6(q) + ".Consumer";
        case F0:
          var H = $;
          return s6(H._context) + ".Provider";
        case I0:
          return "DehydratedFragment";
        case r:
          return B8($, $.render, "ForwardRef");
        case g:
          return "Fragment";
        case R:
          return $;
        case D:
          return "Portal";
        case w:
          return "Root";
        case V:
          return "Text";
        case M0:
          return h0($);
        case s:
          if ($ === PX)
            return "StrictMode";
          return "Mode";
        case Y0:
          return "Offscreen";
        case J0:
          return "Profiler";
        case o:
          return "Scope";
        case l:
          return "Suspense";
        case p:
          return "SuspenseList";
        case Y1:
          return "TracingMarker";
        case F:
        case N:
        case c0:
        case L:
        case t:
        case $0:
          if (typeof $ === "function")
            return $.displayName || $.name || null;
          if (typeof $ === "string")
            return $;
          break;
      }
      return null;
    }
    var GQ = Q.ReactDebugCurrentFrame, z8 = null, MX = !1;
    function bZ() {
      {
        if (z8 === null)
          return null;
        var Z = z8._debugOwner;
        if (Z !== null && typeof Z !== "undefined")
          return V0(Z);
      }
      return null;
    }
    function AK() {
      {
        if (z8 === null)
          return "";
        return _0(z8);
      }
    }
    function N8() {
      GQ.getCurrentStack = null, z8 = null, MX = !1;
    }
    function w6(Z) {
      GQ.getCurrentStack = Z === null ? null : AK, z8 = Z, MX = !1;
    }
    function LK() {
      return z8;
    }
    function dQ(Z) {
      MX = Z;
    }
    function VQ(Z) {
      return "" + Z;
    }
    function DX(Z) {
      switch (typeof Z) {
        case "boolean":
        case "number":
        case "string":
        case "undefined":
          return Z;
        case "object":
          return W8(Z), Z;
        default:
          return "";
      }
    }
    var G7 = {
      button: !0,
      checkbox: !0,
      image: !0,
      hidden: !0,
      radio: !0,
      reset: !0,
      submit: !0
    };
    function i$(Z, X) {
      {
        if (!(G7[X.type] || X.onChange || X.onInput || X.readOnly || X.disabled || X.value == null))
          K("You provided a `value` prop to a form field without an `onChange` handler. This will render a read-only field. If the field should be mutable use `defaultValue`. Otherwise, set either `onChange` or `readOnly`.");
        if (!(X.onChange || X.readOnly || X.disabled || X.checked == null))
          K("You provided a `checked` prop to a form field without an `onChange` handler. This will render a read-only field. If the field should be mutable use `defaultChecked`. Otherwise, set either `onChange` or `readOnly`.");
      }
    }
    function dJ(Z) {
      var { type: X, nodeName: $ } = Z;
      return $ && $.toLowerCase() === "input" && (X === "checkbox" || X === "radio");
    }
    function OK(Z) {
      return Z._valueTracker;
    }
    function h4(Z) {
      Z._valueTracker = null;
    }
    function wK(Z) {
      var X = "";
      if (!Z)
        return X;
      if (dJ(Z))
        X = Z.checked ? "true" : "false";
      else
        X = Z.value;
      return X;
    }
    function MK(Z) {
      var X = dJ(Z) ? "checked" : "value", $ = Object.getOwnPropertyDescriptor(Z.constructor.prototype, X);
      W8(Z[X]);
      var q = "" + Z[X];
      if (Z.hasOwnProperty(X) || typeof $ === "undefined" || typeof $.get !== "function" || typeof $.set !== "function")
        return;
      var { get: H, set: G } = $;
      Object.defineProperty(Z, X, {
        configurable: !0,
        get: function() {
          return H.call(this);
        },
        set: function(U) {
          W8(U), q = "" + U, G.call(this, U);
        }
      }), Object.defineProperty(Z, X, {
        enumerable: $.enumerable
      });
      var E = {
        getValue: function() {
          return q;
        },
        setValue: function(U) {
          W8(U), q = "" + U;
        },
        stopTracking: function() {
          h4(Z), delete Z[X];
        }
      };
      return E;
    }
    function oX(Z) {
      if (OK(Z))
        return;
      Z._valueTracker = MK(Z);
    }
    function t$(Z) {
      if (!Z)
        return !1;
      var X = OK(Z);
      if (!X)
        return !0;
      var $ = X.getValue(), q = wK(Z);
      if (q !== $)
        return X.setValue(q), !0;
      return !1;
    }
    function y4(Z) {
      if (Z = Z || (typeof document !== "undefined" ? document : void 0), typeof Z === "undefined")
        return null;
      try {
        return Z.activeElement || Z.body;
      } catch (X) {
        return Z.body;
      }
    }
    var e$ = !1, DK = !1, kK = !1, RK = !1;
    function jK(Z) {
      var X = Z.type === "checkbox" || Z.type === "radio";
      return X ? Z.checked != null : Z.value != null;
    }
    function A(Z, X) {
      var $ = Z, q = X.checked, H = K1({}, X, {
        defaultChecked: void 0,
        defaultValue: void 0,
        value: void 0,
        checked: q != null ? q : $._wrapperState.initialChecked
      });
      return H;
    }
    function j(Z, X) {
      {
        if (i$("input", X), X.checked !== void 0 && X.defaultChecked !== void 0 && !DK)
          K("%s contains an input of type %s with both checked and defaultChecked props. Input elements must be either controlled or uncontrolled (specify either the checked prop, or the defaultChecked prop, but not both). Decide between using a controlled or uncontrolled input element and remove one of these props. More info: https://reactjs.org/link/controlled-components", bZ() || "A component", X.type), DK = !0;
        if (X.value !== void 0 && X.defaultValue !== void 0 && !e$)
          K("%s contains an input of type %s with both value and defaultValue props. Input elements must be either controlled or uncontrolled (specify either the value prop, or the defaultValue prop, but not both). Decide between using a controlled or uncontrolled input element and remove one of these props. More info: https://reactjs.org/link/controlled-components", bZ() || "A component", X.type), e$ = !0;
      }
      var $ = Z, q = X.defaultValue == null ? "" : X.defaultValue;
      $._wrapperState = {
        initialChecked: X.checked != null ? X.checked : X.defaultChecked,
        initialValue: DX(X.value != null ? X.value : q),
        controlled: jK(X)
      };
    }
    function x(Z, X) {
      var $ = Z, q = X.checked;
      if (q != null)
        BQ($, "checked", q, !1);
    }
    function m(Z, X) {
      var $ = Z;
      {
        var q = jK(X);
        if (!$._wrapperState.controlled && q && !RK)
          K("A component is changing an uncontrolled input to be controlled. This is likely caused by the value changing from undefined to a defined value, which should not happen. Decide between using a controlled or uncontrolled input element for the lifetime of the component. More info: https://reactjs.org/link/controlled-components"), RK = !0;
        if ($._wrapperState.controlled && !q && !kK)
          K("A component is changing a controlled input to be uncontrolled. This is likely caused by the value changing from a defined to undefined, which should not happen. Decide between using a controlled or uncontrolled input element for the lifetime of the component. More info: https://reactjs.org/link/controlled-components"), kK = !0;
      }
      x(Z, X);
      var H = DX(X.value), G = X.type;
      if (H != null) {
        if (G === "number") {
          if (H === 0 && $.value === "" || $.value != H)
            $.value = VQ(H);
        } else if ($.value !== VQ(H))
          $.value = VQ(H);
      } else if (G === "submit" || G === "reset") {
        $.removeAttribute("value");
        return;
      }
      if (X.hasOwnProperty("value"))
        m0($, X.type, H);
      else if (X.hasOwnProperty("defaultValue"))
        m0($, X.type, DX(X.defaultValue));
      if (X.checked == null && X.defaultChecked != null)
        $.defaultChecked = !!X.defaultChecked;
    }
    function e(Z, X, $) {
      var q = Z;
      if (X.hasOwnProperty("value") || X.hasOwnProperty("defaultValue")) {
        var H = X.type, G = H === "submit" || H === "reset";
        if (G && (X.value === void 0 || X.value === null))
          return;
        var E = VQ(q._wrapperState.initialValue);
        if (!$) {
          if (E !== q.value)
            q.value = E;
        }
        q.defaultValue = E;
      }
      var U = q.name;
      if (U !== "")
        q.name = "";
      if (q.defaultChecked = !q.defaultChecked, q.defaultChecked = !!q._wrapperState.initialChecked, U !== "")
        q.name = U;
    }
    function T0(Z, X) {
      var $ = Z;
      m($, X), O0($, X);
    }
    function O0(Z, X) {
      var $ = X.name;
      if (X.type === "radio" && $ != null) {
        var q = Z;
        while (q.parentNode)
          q = q.parentNode;
        h6($, "name");
        var H = q.querySelectorAll("input[name=" + JSON.stringify("" + $) + '][type="radio"]');
        for (var G = 0;G < H.length; G++) {
          var E = H[G];
          if (E === Z || E.form !== Z.form)
            continue;
          var U = N9(E);
          if (!U)
            throw new Error("ReactDOMInput: Mixing React and non-React radio inputs with the same `name` is not supported.");
          t$(E), m(E, U);
        }
      }
    }
    function m0(Z, X, $) {
      if (X !== "number" || y4(Z.ownerDocument) !== Z) {
        if ($ == null)
          Z.defaultValue = VQ(Z._wrapperState.initialValue);
        else if (Z.defaultValue !== VQ($))
          Z.defaultValue = VQ($);
      }
    }
    var P1 = !1, m1 = !1, e1 = !1;
    function Q6(Z, X) {
      {
        if (X.value == null) {
          if (typeof X.children === "object" && X.children !== null)
            A3.Children.forEach(X.children, function($) {
              if ($ == null)
                return;
              if (typeof $ === "string" || typeof $ === "number")
                return;
              if (!m1)
                m1 = !0, K("Cannot infer the option value of complex children. Pass a `value` prop or use a plain string as children to <option>.");
            });
          else if (X.dangerouslySetInnerHTML != null) {
            if (!e1)
              e1 = !0, K("Pass a `value` prop if you set dangerouslyInnerHTML so React knows which value should be selected.");
          }
        }
        if (X.selected != null && !P1)
          K("Use the `defaultValue` or `value` props on <select> instead of setting `selected` on <option>."), P1 = !0;
      }
    }
    function q6(Z, X) {
      if (X.value != null)
        Z.setAttribute("value", VQ(DX(X.value)));
    }
    var R6 = Array.isArray;
    function S1(Z) {
      return R6(Z);
    }
    var lJ = !1;
    function QY() {
      var Z = bZ();
      if (Z)
        return `

Check the render method of \`` + Z + "`.";
      return "";
    }
    var mq = ["value", "defaultValue"];
    function z7(Z) {
      {
        i$("select", Z);
        for (var X = 0;X < mq.length; X++) {
          var $ = mq[X];
          if (Z[$] == null)
            continue;
          var q = S1(Z[$]);
          if (Z.multiple && !q)
            K("The `%s` prop supplied to <select> must be an array if `multiple` is true.%s", $, QY());
          else if (!Z.multiple && q)
            K("The `%s` prop supplied to <select> must be a scalar value if `multiple` is false.%s", $, QY());
        }
      }
    }
    function aX(Z, X, $, q) {
      var H = Z.options;
      if (X) {
        var G = $, E = {};
        for (var U = 0;U < G.length; U++)
          E["$" + G[U]] = !0;
        for (var P = 0;P < H.length; P++) {
          var O = E.hasOwnProperty("$" + H[P].value);
          if (H[P].selected !== O)
            H[P].selected = O;
          if (O && q)
            H[P].defaultSelected = !0;
        }
      } else {
        var k = VQ(DX($)), C = null;
        for (var B = 0;B < H.length; B++) {
          if (H[B].value === k) {
            if (H[B].selected = !0, q)
              H[B].defaultSelected = !0;
            return;
          }
          if (C === null && !H[B].disabled)
            C = H[B];
        }
        if (C !== null)
          C.selected = !0;
      }
    }
    function bq(Z, X) {
      return K1({}, X, {
        value: void 0
      });
    }
    function uq(Z, X) {
      var $ = Z;
      if (z7(X), $._wrapperState = {
        wasMultiple: !!X.multiple
      }, X.value !== void 0 && X.defaultValue !== void 0 && !lJ)
        K("Select elements must be either controlled or uncontrolled (specify either the value prop, or the defaultValue prop, but not both). Decide between using a controlled or uncontrolled select element and remove one of these props. More info: https://reactjs.org/link/controlled-components"), lJ = !0;
    }
    function N7(Z, X) {
      var $ = Z;
      $.multiple = !!X.multiple;
      var q = X.value;
      if (q != null)
        aX($, !!X.multiple, q, !1);
      else if (X.defaultValue != null)
        aX($, !!X.multiple, X.defaultValue, !0);
    }
    function rR(Z, X) {
      var $ = Z, q = $._wrapperState.wasMultiple;
      $._wrapperState.wasMultiple = !!X.multiple;
      var H = X.value;
      if (H != null)
        aX($, !!X.multiple, H, !1);
      else if (q !== !!X.multiple)
        if (X.defaultValue != null)
          aX($, !!X.multiple, X.defaultValue, !0);
        else
          aX($, !!X.multiple, X.multiple ? [] : "", !1);
    }
    function iR(Z, X) {
      var $ = Z, q = X.value;
      if (q != null)
        aX($, !!X.multiple, q, !1);
    }
    var UU = !1;
    function E7(Z, X) {
      var $ = Z;
      if (X.dangerouslySetInnerHTML != null)
        throw new Error("`dangerouslySetInnerHTML` does not make sense on <textarea>.");
      var q = K1({}, X, {
        value: void 0,
        defaultValue: void 0,
        children: VQ($._wrapperState.initialValue)
      });
      return q;
    }
    function PU(Z, X) {
      var $ = Z;
      if (i$("textarea", X), X.value !== void 0 && X.defaultValue !== void 0 && !UU)
        K("%s contains a textarea with both value and defaultValue props. Textarea elements must be either controlled or uncontrolled (specify either the value prop, or the defaultValue prop, but not both). Decide between using a controlled or uncontrolled textarea and remove one of these props. More info: https://reactjs.org/link/controlled-components", bZ() || "A component"), UU = !0;
      var q = X.value;
      if (q == null) {
        var { children: H, defaultValue: G } = X;
        if (H != null) {
          K("Use the `defaultValue` or `value` props instead of setting children on <textarea>.");
          {
            if (G != null)
              throw new Error("If you supply `defaultValue` on a <textarea>, do not pass children.");
            if (S1(H)) {
              if (H.length > 1)
                throw new Error("<textarea> can only have at most one child.");
              H = H[0];
            }
            G = H;
          }
        }
        if (G == null)
          G = "";
        q = G;
      }
      $._wrapperState = {
        initialValue: DX(q)
      };
    }
    function AU(Z, X) {
      var $ = Z, q = DX(X.value), H = DX(X.defaultValue);
      if (q != null) {
        var G = VQ(q);
        if (G !== $.value)
          $.value = G;
        if (X.defaultValue == null && $.defaultValue !== G)
          $.defaultValue = G;
      }
      if (H != null)
        $.defaultValue = VQ(H);
    }
    function LU(Z, X) {
      var $ = Z, q = $.textContent;
      if (q === $._wrapperState.initialValue) {
        if (q !== "" && q !== null)
          $.value = q;
      }
    }
    function tR(Z, X) {
      AU(Z, X);
    }
    var rX = "http://www.w3.org/1999/xhtml", eR = "http://www.w3.org/1998/Math/MathML", F7 = "http://www.w3.org/2000/svg";
    function U7(Z) {
      switch (Z) {
        case "svg":
          return F7;
        case "math":
          return eR;
        default:
          return rX;
      }
    }
    function P7(Z, X) {
      if (Z == null || Z === rX)
        return U7(X);
      if (Z === F7 && X === "foreignObject")
        return rX;
      return Z;
    }
    var Qj = function(Z) {
      if (typeof MSApp !== "undefined" && MSApp.execUnsafeLocalFunction)
        return function(X, $, q, H) {
          MSApp.execUnsafeLocalFunction(function() {
            return Z(X, $, q, H);
          });
        };
      else
        return Z;
    }, BK, OU = Qj(function(Z, X) {
      if (Z.namespaceURI === F7) {
        if (!("innerHTML" in Z)) {
          BK = BK || document.createElement("div"), BK.innerHTML = "<svg>" + X.valueOf().toString() + "</svg>";
          var $ = BK.firstChild;
          while (Z.firstChild)
            Z.removeChild(Z.firstChild);
          while ($.firstChild)
            Z.appendChild($.firstChild);
          return;
        }
      }
      Z.innerHTML = X;
    }), SQ = 1, iX = 3, f6 = 8, tX = 9, A7 = 11, CK = function(Z, X) {
      if (X) {
        var $ = Z.firstChild;
        if ($ && $ === Z.lastChild && $.nodeType === iX) {
          $.nodeValue = X;
          return;
        }
      }
      Z.textContent = X;
    }, Zj = {
      animation: ["animationDelay", "animationDirection", "animationDuration", "animationFillMode", "animationIterationCount", "animationName", "animationPlayState", "animationTimingFunction"],
      background: ["backgroundAttachment", "backgroundClip", "backgroundColor", "backgroundImage", "backgroundOrigin", "backgroundPositionX", "backgroundPositionY", "backgroundRepeat", "backgroundSize"],
      backgroundPosition: ["backgroundPositionX", "backgroundPositionY"],
      border: ["borderBottomColor", "borderBottomStyle", "borderBottomWidth", "borderImageOutset", "borderImageRepeat", "borderImageSlice", "borderImageSource", "borderImageWidth", "borderLeftColor", "borderLeftStyle", "borderLeftWidth", "borderRightColor", "borderRightStyle", "borderRightWidth", "borderTopColor", "borderTopStyle", "borderTopWidth"],
      borderBlockEnd: ["borderBlockEndColor", "borderBlockEndStyle", "borderBlockEndWidth"],
      borderBlockStart: ["borderBlockStartColor", "borderBlockStartStyle", "borderBlockStartWidth"],
      borderBottom: ["borderBottomColor", "borderBottomStyle", "borderBottomWidth"],
      borderColor: ["borderBottomColor", "borderLeftColor", "borderRightColor", "borderTopColor"],
      borderImage: ["borderImageOutset", "borderImageRepeat", "borderImageSlice", "borderImageSource", "borderImageWidth"],
      borderInlineEnd: ["borderInlineEndColor", "borderInlineEndStyle", "borderInlineEndWidth"],
      borderInlineStart: ["borderInlineStartColor", "borderInlineStartStyle", "borderInlineStartWidth"],
      borderLeft: ["borderLeftColor", "borderLeftStyle", "borderLeftWidth"],
      borderRadius: ["borderBottomLeftRadius", "borderBottomRightRadius", "borderTopLeftRadius", "borderTopRightRadius"],
      borderRight: ["borderRightColor", "borderRightStyle", "borderRightWidth"],
      borderStyle: ["borderBottomStyle", "borderLeftStyle", "borderRightStyle", "borderTopStyle"],
      borderTop: ["borderTopColor", "borderTopStyle", "borderTopWidth"],
      borderWidth: ["borderBottomWidth", "borderLeftWidth", "borderRightWidth", "borderTopWidth"],
      columnRule: ["columnRuleColor", "columnRuleStyle", "columnRuleWidth"],
      columns: ["columnCount", "columnWidth"],
      flex: ["flexBasis", "flexGrow", "flexShrink"],
      flexFlow: ["flexDirection", "flexWrap"],
      font: ["fontFamily", "fontFeatureSettings", "fontKerning", "fontLanguageOverride", "fontSize", "fontSizeAdjust", "fontStretch", "fontStyle", "fontVariant", "fontVariantAlternates", "fontVariantCaps", "fontVariantEastAsian", "fontVariantLigatures", "fontVariantNumeric", "fontVariantPosition", "fontWeight", "lineHeight"],
      fontVariant: ["fontVariantAlternates", "fontVariantCaps", "fontVariantEastAsian", "fontVariantLigatures", "fontVariantNumeric", "fontVariantPosition"],
      gap: ["columnGap", "rowGap"],
      grid: ["gridAutoColumns", "gridAutoFlow", "gridAutoRows", "gridTemplateAreas", "gridTemplateColumns", "gridTemplateRows"],
      gridArea: ["gridColumnEnd", "gridColumnStart", "gridRowEnd", "gridRowStart"],
      gridColumn: ["gridColumnEnd", "gridColumnStart"],
      gridColumnGap: ["columnGap"],
      gridGap: ["columnGap", "rowGap"],
      gridRow: ["gridRowEnd", "gridRowStart"],
      gridRowGap: ["rowGap"],
      gridTemplate: ["gridTemplateAreas", "gridTemplateColumns", "gridTemplateRows"],
      listStyle: ["listStyleImage", "listStylePosition", "listStyleType"],
      margin: ["marginBottom", "marginLeft", "marginRight", "marginTop"],
      marker: ["markerEnd", "markerMid", "markerStart"],
      mask: ["maskClip", "maskComposite", "maskImage", "maskMode", "maskOrigin", "maskPositionX", "maskPositionY", "maskRepeat", "maskSize"],
      maskPosition: ["maskPositionX", "maskPositionY"],
      outline: ["outlineColor", "outlineStyle", "outlineWidth"],
      overflow: ["overflowX", "overflowY"],
      padding: ["paddingBottom", "paddingLeft", "paddingRight", "paddingTop"],
      placeContent: ["alignContent", "justifyContent"],
      placeItems: ["alignItems", "justifyItems"],
      placeSelf: ["alignSelf", "justifySelf"],
      textDecoration: ["textDecorationColor", "textDecorationLine", "textDecorationStyle"],
      textEmphasis: ["textEmphasisColor", "textEmphasisStyle"],
      transition: ["transitionDelay", "transitionDuration", "transitionProperty", "transitionTimingFunction"],
      wordWrap: ["overflowWrap"]
    }, cq = {
      animationIterationCount: !0,
      aspectRatio: !0,
      borderImageOutset: !0,
      borderImageSlice: !0,
      borderImageWidth: !0,
      boxFlex: !0,
      boxFlexGroup: !0,
      boxOrdinalGroup: !0,
      columnCount: !0,
      columns: !0,
      flex: !0,
      flexGrow: !0,
      flexPositive: !0,
      flexShrink: !0,
      flexNegative: !0,
      flexOrder: !0,
      gridArea: !0,
      gridRow: !0,
      gridRowEnd: !0,
      gridRowSpan: !0,
      gridRowStart: !0,
      gridColumn: !0,
      gridColumnEnd: !0,
      gridColumnSpan: !0,
      gridColumnStart: !0,
      fontWeight: !0,
      lineClamp: !0,
      lineHeight: !0,
      opacity: !0,
      order: !0,
      orphans: !0,
      tabSize: !0,
      widows: !0,
      zIndex: !0,
      zoom: !0,
      fillOpacity: !0,
      floodOpacity: !0,
      stopOpacity: !0,
      strokeDasharray: !0,
      strokeDashoffset: !0,
      strokeMiterlimit: !0,
      strokeOpacity: !0,
      strokeWidth: !0
    };
    function Xj(Z, X) {
      return Z + X.charAt(0).toUpperCase() + X.substring(1);
    }
    var Jj = ["Webkit", "ms", "Moz", "O"];
    Object.keys(cq).forEach(function(Z) {
      Jj.forEach(function(X) {
        cq[Xj(X, Z)] = cq[Z];
      });
    });
    function L7(Z, X, $) {
      var q = X == null || typeof X === "boolean" || X === "";
      if (q)
        return "";
      if (!$ && typeof X === "number" && X !== 0 && !(cq.hasOwnProperty(Z) && cq[Z]))
        return X + "px";
      return k8(X, Z), ("" + X).trim();
    }
    var $j = /([A-Z])/g, Yj = /^ms-/;
    function qj(Z) {
      return Z.replace($j, "-$1").toLowerCase().replace(Yj, "-ms-");
    }
    var wU = function() {};
    {
      var Wj = /^(?:webkit|moz|o)[A-Z]/, Kj = /^-ms-/, Hj = /-(.)/g, MU = /;\s*$/, ZY = {}, O7 = {}, DU = !1, kU = !1, Gj = function(Z) {
        return Z.replace(Hj, function(X, $) {
          return $.toUpperCase();
        });
      }, zj = function(Z) {
        if (ZY.hasOwnProperty(Z) && ZY[Z])
          return;
        ZY[Z] = !0, K("Unsupported style property %s. Did you mean %s?", Z, Gj(Z.replace(Kj, "ms-")));
      }, Nj = function(Z) {
        if (ZY.hasOwnProperty(Z) && ZY[Z])
          return;
        ZY[Z] = !0, K("Unsupported vendor-prefixed style property %s. Did you mean %s?", Z, Z.charAt(0).toUpperCase() + Z.slice(1));
      }, Ej = function(Z, X) {
        if (O7.hasOwnProperty(X) && O7[X])
          return;
        O7[X] = !0, K(`Style property values shouldn't contain a semicolon. Try "%s: %s" instead.`, Z, X.replace(MU, ""));
      }, Fj = function(Z, X) {
        if (DU)
          return;
        DU = !0, K("`NaN` is an invalid value for the `%s` css style property.", Z);
      }, Uj = function(Z, X) {
        if (kU)
          return;
        kU = !0, K("`Infinity` is an invalid value for the `%s` css style property.", Z);
      };
      wU = function(Z, X) {
        if (Z.indexOf("-") > -1)
          zj(Z);
        else if (Wj.test(Z))
          Nj(Z);
        else if (MU.test(X))
          Ej(Z, X);
        if (typeof X === "number") {
          if (isNaN(X))
            Fj(Z, X);
          else if (!isFinite(X))
            Uj(Z, X);
        }
      };
    }
    var Pj = wU;
    function Aj(Z) {
      {
        var X = "", $ = "";
        for (var q in Z) {
          if (!Z.hasOwnProperty(q))
            continue;
          var H = Z[q];
          if (H != null) {
            var G = q.indexOf("--") === 0;
            X += $ + (G ? q : qj(q)) + ":", X += L7(q, H, G), $ = ";";
          }
        }
        return X || null;
      }
    }
    function RU(Z, X) {
      var $ = Z.style;
      for (var q in X) {
        if (!X.hasOwnProperty(q))
          continue;
        var H = q.indexOf("--") === 0;
        if (!H)
          Pj(q, X[q]);
        var G = L7(q, X[q], H);
        if (q === "float")
          q = "cssFloat";
        if (H)
          $.setProperty(q, G);
        else
          $[q] = G;
      }
    }
    function Lj(Z) {
      return Z == null || typeof Z === "boolean" || Z === "";
    }
    function jU(Z) {
      var X = {};
      for (var $ in Z) {
        var q = Zj[$] || [$];
        for (var H = 0;H < q.length; H++)
          X[q[H]] = $;
      }
      return X;
    }
    function Oj(Z, X) {
      {
        if (!X)
          return;
        var $ = jU(Z), q = jU(X), H = {};
        for (var G in $) {
          var E = $[G], U = q[G];
          if (U && E !== U) {
            var P = E + "," + U;
            if (H[P])
              continue;
            H[P] = !0, K("%s a style property during rerender (%s) when a conflicting property is set (%s) can lead to styling bugs. To avoid this, don't mix shorthand and non-shorthand properties for the same value; instead, replace the shorthand with separate values.", Lj(Z[E]) ? "Removing" : "Updating", E, U);
          }
        }
      }
    }
    var wj = {
      area: !0,
      base: !0,
      br: !0,
      col: !0,
      embed: !0,
      hr: !0,
      img: !0,
      input: !0,
      keygen: !0,
      link: !0,
      meta: !0,
      param: !0,
      source: !0,
      track: !0,
      wbr: !0
    }, Mj = K1({
      menuitem: !0
    }, wj), Dj = "__html";
    function w7(Z, X) {
      if (!X)
        return;
      if (Mj[Z]) {
        if (X.children != null || X.dangerouslySetInnerHTML != null)
          throw new Error(Z + " is a void element tag and must neither have `children` nor use `dangerouslySetInnerHTML`.");
      }
      if (X.dangerouslySetInnerHTML != null) {
        if (X.children != null)
          throw new Error("Can only set one of `children` or `props.dangerouslySetInnerHTML`.");
        if (typeof X.dangerouslySetInnerHTML !== "object" || !(Dj in X.dangerouslySetInnerHTML))
          throw new Error("`props.dangerouslySetInnerHTML` must be in the form `{__html: ...}`. Please visit https://reactjs.org/link/dangerously-set-inner-html for more information.");
      }
      if (!X.suppressContentEditableWarning && X.contentEditable && X.children != null)
        K("A component is `contentEditable` and contains `children` managed by React. It is now your responsibility to guarantee that none of those nodes are unexpectedly modified or duplicated. This is probably not intentional.");
      if (X.style != null && typeof X.style !== "object")
        throw new Error("The `style` prop expects a mapping from style properties to values, not a string. For example, style={{marginRight: spacing + 'em'}} when using JSX.");
    }
    function nJ(Z, X) {
      if (Z.indexOf("-") === -1)
        return typeof X.is === "string";
      switch (Z) {
        case "annotation-xml":
        case "color-profile":
        case "font-face":
        case "font-face-src":
        case "font-face-uri":
        case "font-face-format":
        case "font-face-name":
        case "missing-glyph":
          return !1;
        default:
          return !0;
      }
    }
    var VK = {
      accept: "accept",
      acceptcharset: "acceptCharset",
      "accept-charset": "acceptCharset",
      accesskey: "accessKey",
      action: "action",
      allowfullscreen: "allowFullScreen",
      alt: "alt",
      as: "as",
      async: "async",
      autocapitalize: "autoCapitalize",
      autocomplete: "autoComplete",
      autocorrect: "autoCorrect",
      autofocus: "autoFocus",
      autoplay: "autoPlay",
      autosave: "autoSave",
      capture: "capture",
      cellpadding: "cellPadding",
      cellspacing: "cellSpacing",
      challenge: "challenge",
      charset: "charSet",
      checked: "checked",
      children: "children",
      cite: "cite",
      class: "className",
      classid: "classID",
      classname: "className",
      cols: "cols",
      colspan: "colSpan",
      content: "content",
      contenteditable: "contentEditable",
      contextmenu: "contextMenu",
      controls: "controls",
      controlslist: "controlsList",
      coords: "coords",
      crossorigin: "crossOrigin",
      dangerouslysetinnerhtml: "dangerouslySetInnerHTML",
      data: "data",
      datetime: "dateTime",
      default: "default",
      defaultchecked: "defaultChecked",
      defaultvalue: "defaultValue",
      defer: "defer",
      dir: "dir",
      disabled: "disabled",
      disablepictureinpicture: "disablePictureInPicture",
      disableremoteplayback: "disableRemotePlayback",
      download: "download",
      draggable: "draggable",
      enctype: "encType",
      enterkeyhint: "enterKeyHint",
      for: "htmlFor",
      form: "form",
      formmethod: "formMethod",
      formaction: "formAction",
      formenctype: "formEncType",
      formnovalidate: "formNoValidate",
      formtarget: "formTarget",
      frameborder: "frameBorder",
      headers: "headers",
      height: "height",
      hidden: "hidden",
      high: "high",
      href: "href",
      hreflang: "hrefLang",
      htmlfor: "htmlFor",
      httpequiv: "httpEquiv",
      "http-equiv": "httpEquiv",
      icon: "icon",
      id: "id",
      imagesizes: "imageSizes",
      imagesrcset: "imageSrcSet",
      innerhtml: "innerHTML",
      inputmode: "inputMode",
      integrity: "integrity",
      is: "is",
      itemid: "itemID",
      itemprop: "itemProp",
      itemref: "itemRef",
      itemscope: "itemScope",
      itemtype: "itemType",
      keyparams: "keyParams",
      keytype: "keyType",
      kind: "kind",
      label: "label",
      lang: "lang",
      list: "list",
      loop: "loop",
      low: "low",
      manifest: "manifest",
      marginwidth: "marginWidth",
      marginheight: "marginHeight",
      max: "max",
      maxlength: "maxLength",
      media: "media",
      mediagroup: "mediaGroup",
      method: "method",
      min: "min",
      minlength: "minLength",
      multiple: "multiple",
      muted: "muted",
      name: "name",
      nomodule: "noModule",
      nonce: "nonce",
      novalidate: "noValidate",
      open: "open",
      optimum: "optimum",
      pattern: "pattern",
      placeholder: "placeholder",
      playsinline: "playsInline",
      poster: "poster",
      preload: "preload",
      profile: "profile",
      radiogroup: "radioGroup",
      readonly: "readOnly",
      referrerpolicy: "referrerPolicy",
      rel: "rel",
      required: "required",
      reversed: "reversed",
      role: "role",
      rows: "rows",
      rowspan: "rowSpan",
      sandbox: "sandbox",
      scope: "scope",
      scoped: "scoped",
      scrolling: "scrolling",
      seamless: "seamless",
      selected: "selected",
      shape: "shape",
      size: "size",
      sizes: "sizes",
      span: "span",
      spellcheck: "spellCheck",
      src: "src",
      srcdoc: "srcDoc",
      srclang: "srcLang",
      srcset: "srcSet",
      start: "start",
      step: "step",
      style: "style",
      summary: "summary",
      tabindex: "tabIndex",
      target: "target",
      title: "title",
      type: "type",
      usemap: "useMap",
      value: "value",
      width: "width",
      wmode: "wmode",
      wrap: "wrap",
      about: "about",
      accentheight: "accentHeight",
      "accent-height": "accentHeight",
      accumulate: "accumulate",
      additive: "additive",
      alignmentbaseline: "alignmentBaseline",
      "alignment-baseline": "alignmentBaseline",
      allowreorder: "allowReorder",
      alphabetic: "alphabetic",
      amplitude: "amplitude",
      arabicform: "arabicForm",
      "arabic-form": "arabicForm",
      ascent: "ascent",
      attributename: "attributeName",
      attributetype: "attributeType",
      autoreverse: "autoReverse",
      azimuth: "azimuth",
      basefrequency: "baseFrequency",
      baselineshift: "baselineShift",
      "baseline-shift": "baselineShift",
      baseprofile: "baseProfile",
      bbox: "bbox",
      begin: "begin",
      bias: "bias",
      by: "by",
      calcmode: "calcMode",
      capheight: "capHeight",
      "cap-height": "capHeight",
      clip: "clip",
      clippath: "clipPath",
      "clip-path": "clipPath",
      clippathunits: "clipPathUnits",
      cliprule: "clipRule",
      "clip-rule": "clipRule",
      color: "color",
      colorinterpolation: "colorInterpolation",
      "color-interpolation": "colorInterpolation",
      colorinterpolationfilters: "colorInterpolationFilters",
      "color-interpolation-filters": "colorInterpolationFilters",
      colorprofile: "colorProfile",
      "color-profile": "colorProfile",
      colorrendering: "colorRendering",
      "color-rendering": "colorRendering",
      contentscripttype: "contentScriptType",
      contentstyletype: "contentStyleType",
      cursor: "cursor",
      cx: "cx",
      cy: "cy",
      d: "d",
      datatype: "datatype",
      decelerate: "decelerate",
      descent: "descent",
      diffuseconstant: "diffuseConstant",
      direction: "direction",
      display: "display",
      divisor: "divisor",
      dominantbaseline: "dominantBaseline",
      "dominant-baseline": "dominantBaseline",
      dur: "dur",
      dx: "dx",
      dy: "dy",
      edgemode: "edgeMode",
      elevation: "elevation",
      enablebackground: "enableBackground",
      "enable-background": "enableBackground",
      end: "end",
      exponent: "exponent",
      externalresourcesrequired: "externalResourcesRequired",
      fill: "fill",
      fillopacity: "fillOpacity",
      "fill-opacity": "fillOpacity",
      fillrule: "fillRule",
      "fill-rule": "fillRule",
      filter: "filter",
      filterres: "filterRes",
      filterunits: "filterUnits",
      floodopacity: "floodOpacity",
      "flood-opacity": "floodOpacity",
      floodcolor: "floodColor",
      "flood-color": "floodColor",
      focusable: "focusable",
      fontfamily: "fontFamily",
      "font-family": "fontFamily",
      fontsize: "fontSize",
      "font-size": "fontSize",
      fontsizeadjust: "fontSizeAdjust",
      "font-size-adjust": "fontSizeAdjust",
      fontstretch: "fontStretch",
      "font-stretch": "fontStretch",
      fontstyle: "fontStyle",
      "font-style": "fontStyle",
      fontvariant: "fontVariant",
      "font-variant": "fontVariant",
      fontweight: "fontWeight",
      "font-weight": "fontWeight",
      format: "format",
      from: "from",
      fx: "fx",
      fy: "fy",
      g1: "g1",
      g2: "g2",
      glyphname: "glyphName",
      "glyph-name": "glyphName",
      glyphorientationhorizontal: "glyphOrientationHorizontal",
      "glyph-orientation-horizontal": "glyphOrientationHorizontal",
      glyphorientationvertical: "glyphOrientationVertical",
      "glyph-orientation-vertical": "glyphOrientationVertical",
      glyphref: "glyphRef",
      gradienttransform: "gradientTransform",
      gradientunits: "gradientUnits",
      hanging: "hanging",
      horizadvx: "horizAdvX",
      "horiz-adv-x": "horizAdvX",
      horizoriginx: "horizOriginX",
      "horiz-origin-x": "horizOriginX",
      ideographic: "ideographic",
      imagerendering: "imageRendering",
      "image-rendering": "imageRendering",
      in2: "in2",
      in: "in",
      inlist: "inlist",
      intercept: "intercept",
      k1: "k1",
      k2: "k2",
      k3: "k3",
      k4: "k4",
      k: "k",
      kernelmatrix: "kernelMatrix",
      kernelunitlength: "kernelUnitLength",
      kerning: "kerning",
      keypoints: "keyPoints",
      keysplines: "keySplines",
      keytimes: "keyTimes",
      lengthadjust: "lengthAdjust",
      letterspacing: "letterSpacing",
      "letter-spacing": "letterSpacing",
      lightingcolor: "lightingColor",
      "lighting-color": "lightingColor",
      limitingconeangle: "limitingConeAngle",
      local: "local",
      markerend: "markerEnd",
      "marker-end": "markerEnd",
      markerheight: "markerHeight",
      markermid: "markerMid",
      "marker-mid": "markerMid",
      markerstart: "markerStart",
      "marker-start": "markerStart",
      markerunits: "markerUnits",
      markerwidth: "markerWidth",
      mask: "mask",
      maskcontentunits: "maskContentUnits",
      maskunits: "maskUnits",
      mathematical: "mathematical",
      mode: "mode",
      numoctaves: "numOctaves",
      offset: "offset",
      opacity: "opacity",
      operator: "operator",
      order: "order",
      orient: "orient",
      orientation: "orientation",
      origin: "origin",
      overflow: "overflow",
      overlineposition: "overlinePosition",
      "overline-position": "overlinePosition",
      overlinethickness: "overlineThickness",
      "overline-thickness": "overlineThickness",
      paintorder: "paintOrder",
      "paint-order": "paintOrder",
      panose1: "panose1",
      "panose-1": "panose1",
      pathlength: "pathLength",
      patterncontentunits: "patternContentUnits",
      patterntransform: "patternTransform",
      patternunits: "patternUnits",
      pointerevents: "pointerEvents",
      "pointer-events": "pointerEvents",
      points: "points",
      pointsatx: "pointsAtX",
      pointsaty: "pointsAtY",
      pointsatz: "pointsAtZ",
      prefix: "prefix",
      preservealpha: "preserveAlpha",
      preserveaspectratio: "preserveAspectRatio",
      primitiveunits: "primitiveUnits",
      property: "property",
      r: "r",
      radius: "radius",
      refx: "refX",
      refy: "refY",
      renderingintent: "renderingIntent",
      "rendering-intent": "renderingIntent",
      repeatcount: "repeatCount",
      repeatdur: "repeatDur",
      requiredextensions: "requiredExtensions",
      requiredfeatures: "requiredFeatures",
      resource: "resource",
      restart: "restart",
      result: "result",
      results: "results",
      rotate: "rotate",
      rx: "rx",
      ry: "ry",
      scale: "scale",
      security: "security",
      seed: "seed",
      shaperendering: "shapeRendering",
      "shape-rendering": "shapeRendering",
      slope: "slope",
      spacing: "spacing",
      specularconstant: "specularConstant",
      specularexponent: "specularExponent",
      speed: "speed",
      spreadmethod: "spreadMethod",
      startoffset: "startOffset",
      stddeviation: "stdDeviation",
      stemh: "stemh",
      stemv: "stemv",
      stitchtiles: "stitchTiles",
      stopcolor: "stopColor",
      "stop-color": "stopColor",
      stopopacity: "stopOpacity",
      "stop-opacity": "stopOpacity",
      strikethroughposition: "strikethroughPosition",
      "strikethrough-position": "strikethroughPosition",
      strikethroughthickness: "strikethroughThickness",
      "strikethrough-thickness": "strikethroughThickness",
      string: "string",
      stroke: "stroke",
      strokedasharray: "strokeDasharray",
      "stroke-dasharray": "strokeDasharray",
      strokedashoffset: "strokeDashoffset",
      "stroke-dashoffset": "strokeDashoffset",
      strokelinecap: "strokeLinecap",
      "stroke-linecap": "strokeLinecap",
      strokelinejoin: "strokeLinejoin",
      "stroke-linejoin": "strokeLinejoin",
      strokemiterlimit: "strokeMiterlimit",
      "stroke-miterlimit": "strokeMiterlimit",
      strokewidth: "strokeWidth",
      "stroke-width": "strokeWidth",
      strokeopacity: "strokeOpacity",
      "stroke-opacity": "strokeOpacity",
      suppresscontenteditablewarning: "suppressContentEditableWarning",
      suppresshydrationwarning: "suppressHydrationWarning",
      surfacescale: "surfaceScale",
      systemlanguage: "systemLanguage",
      tablevalues: "tableValues",
      targetx: "targetX",
      targety: "targetY",
      textanchor: "textAnchor",
      "text-anchor": "textAnchor",
      textdecoration: "textDecoration",
      "text-decoration": "textDecoration",
      textlength: "textLength",
      textrendering: "textRendering",
      "text-rendering": "textRendering",
      to: "to",
      transform: "transform",
      typeof: "typeof",
      u1: "u1",
      u2: "u2",
      underlineposition: "underlinePosition",
      "underline-position": "underlinePosition",
      underlinethickness: "underlineThickness",
      "underline-thickness": "underlineThickness",
      unicode: "unicode",
      unicodebidi: "unicodeBidi",
      "unicode-bidi": "unicodeBidi",
      unicoderange: "unicodeRange",
      "unicode-range": "unicodeRange",
      unitsperem: "unitsPerEm",
      "units-per-em": "unitsPerEm",
      unselectable: "unselectable",
      valphabetic: "vAlphabetic",
      "v-alphabetic": "vAlphabetic",
      values: "values",
      vectoreffect: "vectorEffect",
      "vector-effect": "vectorEffect",
      version: "version",
      vertadvy: "vertAdvY",
      "vert-adv-y": "vertAdvY",
      vertoriginx: "vertOriginX",
      "vert-origin-x": "vertOriginX",
      vertoriginy: "vertOriginY",
      "vert-origin-y": "vertOriginY",
      vhanging: "vHanging",
      "v-hanging": "vHanging",
      videographic: "vIdeographic",
      "v-ideographic": "vIdeographic",
      viewbox: "viewBox",
      viewtarget: "viewTarget",
      visibility: "visibility",
      vmathematical: "vMathematical",
      "v-mathematical": "vMathematical",
      vocab: "vocab",
      widths: "widths",
      wordspacing: "wordSpacing",
      "word-spacing": "wordSpacing",
      writingmode: "writingMode",
      "writing-mode": "writingMode",
      x1: "x1",
      x2: "x2",
      x: "x",
      xchannelselector: "xChannelSelector",
      xheight: "xHeight",
      "x-height": "xHeight",
      xlinkactuate: "xlinkActuate",
      "xlink:actuate": "xlinkActuate",
      xlinkarcrole: "xlinkArcrole",
      "xlink:arcrole": "xlinkArcrole",
      xlinkhref: "xlinkHref",
      "xlink:href": "xlinkHref",
      xlinkrole: "xlinkRole",
      "xlink:role": "xlinkRole",
      xlinkshow: "xlinkShow",
      "xlink:show": "xlinkShow",
      xlinktitle: "xlinkTitle",
      "xlink:title": "xlinkTitle",
      xlinktype: "xlinkType",
      "xlink:type": "xlinkType",
      xmlbase: "xmlBase",
      "xml:base": "xmlBase",
      xmllang: "xmlLang",
      "xml:lang": "xmlLang",
      xmlns: "xmlns",
      "xml:space": "xmlSpace",
      xmlnsxlink: "xmlnsXlink",
      "xmlns:xlink": "xmlnsXlink",
      xmlspace: "xmlSpace",
      y1: "y1",
      y2: "y2",
      y: "y",
      ychannelselector: "yChannelSelector",
      z: "z",
      zoomandpan: "zoomAndPan"
    }, BU = {
      "aria-current": 0,
      "aria-description": 0,
      "aria-details": 0,
      "aria-disabled": 0,
      "aria-hidden": 0,
      "aria-invalid": 0,
      "aria-keyshortcuts": 0,
      "aria-label": 0,
      "aria-roledescription": 0,
      "aria-autocomplete": 0,
      "aria-checked": 0,
      "aria-expanded": 0,
      "aria-haspopup": 0,
      "aria-level": 0,
      "aria-modal": 0,
      "aria-multiline": 0,
      "aria-multiselectable": 0,
      "aria-orientation": 0,
      "aria-placeholder": 0,
      "aria-pressed": 0,
      "aria-readonly": 0,
      "aria-required": 0,
      "aria-selected": 0,
      "aria-sort": 0,
      "aria-valuemax": 0,
      "aria-valuemin": 0,
      "aria-valuenow": 0,
      "aria-valuetext": 0,
      "aria-atomic": 0,
      "aria-busy": 0,
      "aria-live": 0,
      "aria-relevant": 0,
      "aria-dropeffect": 0,
      "aria-grabbed": 0,
      "aria-activedescendant": 0,
      "aria-colcount": 0,
      "aria-colindex": 0,
      "aria-colspan": 0,
      "aria-controls": 0,
      "aria-describedby": 0,
      "aria-errormessage": 0,
      "aria-flowto": 0,
      "aria-labelledby": 0,
      "aria-owns": 0,
      "aria-posinset": 0,
      "aria-rowcount": 0,
      "aria-rowindex": 0,
      "aria-rowspan": 0,
      "aria-setsize": 0
    }, XY = {}, kj = new RegExp("^(aria)-[" + jQ + "]*$"), Rj = new RegExp("^(aria)[A-Z][" + jQ + "]*$");
    function jj(Z, X) {
      {
        if (Z0.call(XY, X) && XY[X])
          return !0;
        if (Rj.test(X)) {
          var $ = "aria-" + X.slice(4).toLowerCase(), q = BU.hasOwnProperty($) ? $ : null;
          if (q == null)
            return K("Invalid ARIA attribute `%s`. ARIA attributes follow the pattern aria-* and must be lowercase.", X), XY[X] = !0, !0;
          if (X !== q)
            return K("Invalid ARIA attribute `%s`. Did you mean `%s`?", X, q), XY[X] = !0, !0;
        }
        if (kj.test(X)) {
          var H = X.toLowerCase(), G = BU.hasOwnProperty(H) ? H : null;
          if (G == null)
            return XY[X] = !0, !1;
          if (X !== G)
            return K("Unknown ARIA attribute `%s`. Did you mean `%s`?", X, G), XY[X] = !0, !0;
        }
      }
      return !0;
    }
    function Bj(Z, X) {
      {
        var $ = [];
        for (var q in X) {
          var H = jj(Z, q);
          if (!H)
            $.push(q);
        }
        var G = $.map(function(E) {
          return "`" + E + "`";
        }).join(", ");
        if ($.length === 1)
          K("Invalid aria prop %s on <%s> tag. For details, see https://reactjs.org/link/invalid-aria-props", G, Z);
        else if ($.length > 1)
          K("Invalid aria props %s on <%s> tag. For details, see https://reactjs.org/link/invalid-aria-props", G, Z);
      }
    }
    function Cj(Z, X) {
      if (nJ(Z, X))
        return;
      Bj(Z, X);
    }
    var CU = !1;
    function Vj(Z, X) {
      {
        if (Z !== "input" && Z !== "textarea" && Z !== "select")
          return;
        if (X != null && X.value === null && !CU)
          if (CU = !0, Z === "select" && X.multiple)
            K("`value` prop on `%s` should not be null. Consider using an empty array when `multiple` is set to `true` to clear the component or `undefined` for uncontrolled components.", Z);
          else
            K("`value` prop on `%s` should not be null. Consider using an empty string to clear the component or `undefined` for uncontrolled components.", Z);
      }
    }
    var VU = function() {};
    {
      var zQ = {}, SU = /^on./, Sj = /^on[^A-Z]/, Ij = new RegExp("^(aria)-[" + jQ + "]*$"), _j = new RegExp("^(aria)[A-Z][" + jQ + "]*$");
      VU = function(Z, X, $, q) {
        if (Z0.call(zQ, X) && zQ[X])
          return !0;
        var H = X.toLowerCase();
        if (H === "onfocusin" || H === "onfocusout")
          return K("React uses onFocus and onBlur instead of onFocusIn and onFocusOut. All React events are normalized to bubble, so onFocusIn and onFocusOut are not needed/supported by React."), zQ[X] = !0, !0;
        if (q != null) {
          var { registrationNameDependencies: G, possibleRegistrationNames: E } = q;
          if (G.hasOwnProperty(X))
            return !0;
          var U = E.hasOwnProperty(H) ? E[H] : null;
          if (U != null)
            return K("Invalid event handler property `%s`. Did you mean `%s`?", X, U), zQ[X] = !0, !0;
          if (SU.test(X))
            return K("Unknown event handler property `%s`. It will be ignored.", X), zQ[X] = !0, !0;
        } else if (SU.test(X)) {
          if (Sj.test(X))
            K("Invalid event handler property `%s`. React events use the camelCase naming convention, for example `onClick`.", X);
          return zQ[X] = !0, !0;
        }
        if (Ij.test(X) || _j.test(X))
          return !0;
        if (H === "innerhtml")
          return K("Directly setting property `innerHTML` is not permitted. For more information, lookup documentation on `dangerouslySetInnerHTML`."), zQ[X] = !0, !0;
        if (H === "aria")
          return K("The `aria` attribute is reserved for future use in React. Pass individual `aria-` attributes instead."), zQ[X] = !0, !0;
        if (H === "is" && $ !== null && $ !== void 0 && typeof $ !== "string")
          return K("Received a `%s` for a string attribute `is`. If this is expected, cast the value to a string.", typeof $), zQ[X] = !0, !0;
        if (typeof $ === "number" && isNaN($))
          return K("Received NaN for the `%s` attribute. If this is expected, cast the value to a string.", X), zQ[X] = !0, !0;
        var P = l8(X), O = P !== null && P.type === d6;
        if (VK.hasOwnProperty(H)) {
          var k = VK[H];
          if (k !== X)
            return K("Invalid DOM property `%s`. Did you mean `%s`?", X, k), zQ[X] = !0, !0;
        } else if (!O && X !== H)
          return K("React does not recognize the `%s` prop on a DOM element. If you intentionally want it to appear in the DOM as a custom attribute, spell it as lowercase `%s` instead. If you accidentally passed it from a parent component, remove it from the DOM element.", X, H), zQ[X] = !0, !0;
        if (typeof $ === "boolean" && V6(X, $, P, !1)) {
          if ($)
            K('Received `%s` for a non-boolean attribute `%s`.\n\nIf you want to write it to the DOM, pass a string instead: %s="%s" or %s={value.toString()}.', $, X, X, $, X);
          else
            K('Received `%s` for a non-boolean attribute `%s`.\n\nIf you want to write it to the DOM, pass a string instead: %s="%s" or %s={value.toString()}.\n\nIf you used to conditionally omit it with %s={condition && value}, pass %s={condition ? value : undefined} instead.', $, X, X, $, X, X, X);
          return zQ[X] = !0, !0;
        }
        if (O)
          return !0;
        if (V6(X, $, P, !1))
          return zQ[X] = !0, !1;
        if (($ === "false" || $ === "true") && P !== null && P.type === R8)
          return K("Received the string `%s` for the boolean attribute `%s`. %s Did you mean %s={%s}?", $, X, $ === "false" ? "The browser will interpret it as a truthy value." : 'Although this works, it will not work as expected if you pass the string "false".', X, $), zQ[X] = !0, !0;
        return !0;
      };
    }
    var Tj = function(Z, X, $) {
      {
        var q = [];
        for (var H in X) {
          var G = VU(Z, H, X[H], $);
          if (!G)
            q.push(H);
        }
        var E = q.map(function(U) {
          return "`" + U + "`";
        }).join(", ");
        if (q.length === 1)
          K("Invalid value for prop %s on <%s> tag. Either remove it from the element, or pass a string or number value to keep it in the DOM. For details, see https://reactjs.org/link/attribute-behavior ", E, Z);
        else if (q.length > 1)
          K("Invalid values for props %s on <%s> tag. Either remove them from the element, or pass a string or number value to keep them in the DOM. For details, see https://reactjs.org/link/attribute-behavior ", E, Z);
      }
    };
    function gj(Z, X, $) {
      if (nJ(Z, X))
        return;
      Tj(Z, X, $);
    }
    var IU = 1, M7 = 2, pq = 4, xj = IU | M7 | pq, dq = null;
    function vj(Z) {
      if (dq !== null)
        K("Expected currently replaying event to be null. This error is likely caused by a bug in React. Please file an issue.");
      dq = Z;
    }
    function hj() {
      if (dq === null)
        K("Expected currently replaying event to not be null. This error is likely caused by a bug in React. Please file an issue.");
      dq = null;
    }
    function yj(Z) {
      return Z === dq;
    }
    function D7(Z) {
      var X = Z.target || Z.srcElement || window;
      if (X.correspondingUseElement)
        X = X.correspondingUseElement;
      return X.nodeType === iX ? X.parentNode : X;
    }
    var k7 = null, JY = null, $Y = null;
    function _U(Z) {
      var X = l4(Z);
      if (!X)
        return;
      if (typeof k7 !== "function")
        throw new Error("setRestoreImplementation() needs to be called to handle a target for controlled events. This error is likely caused by a bug in React. Please file an issue.");
      var $ = X.stateNode;
      if ($) {
        var q = N9($);
        k7(X.stateNode, X.type, q);
      }
    }
    function fj(Z) {
      k7 = Z;
    }
    function TU(Z) {
      if (JY)
        if ($Y)
          $Y.push(Z);
        else
          $Y = [Z];
      else
        JY = Z;
    }
    function mj() {
      return JY !== null || $Y !== null;
    }
    function gU() {
      if (!JY)
        return;
      var Z = JY, X = $Y;
      if (JY = null, $Y = null, _U(Z), X)
        for (var $ = 0;$ < X.length; $++)
          _U(X[$]);
    }
    var xU = function(Z, X) {
      return Z(X);
    }, vU = function() {}, R7 = !1;
    function bj() {
      var Z = mj();
      if (Z)
        vU(), gU();
    }
    function hU(Z, X, $) {
      if (R7)
        return Z(X, $);
      R7 = !0;
      try {
        return xU(Z, X, $);
      } finally {
        R7 = !1, bj();
      }
    }
    function uj(Z, X, $) {
      xU = Z, vU = $;
    }
    function cj(Z) {
      return Z === "button" || Z === "input" || Z === "select" || Z === "textarea";
    }
    function pj(Z, X, $) {
      switch (Z) {
        case "onClick":
        case "onClickCapture":
        case "onDoubleClick":
        case "onDoubleClickCapture":
        case "onMouseDown":
        case "onMouseDownCapture":
        case "onMouseMove":
        case "onMouseMoveCapture":
        case "onMouseUp":
        case "onMouseUpCapture":
        case "onMouseEnter":
          return !!($.disabled && cj(X));
        default:
          return !1;
      }
    }
    function lq(Z, X) {
      var $ = Z.stateNode;
      if ($ === null)
        return null;
      var q = N9($);
      if (q === null)
        return null;
      var H = q[X];
      if (pj(X, Z.type, q))
        return null;
      if (H && typeof H !== "function")
        throw new Error("Expected `" + X + "` listener to be a function, instead got a value of `" + typeof H + "` type.");
      return H;
    }
    var j7 = !1;
    if (i1)
      try {
        var nq = {};
        Object.defineProperty(nq, "passive", {
          get: function() {
            j7 = !0;
          }
        }), window.addEventListener("test", nq, nq), window.removeEventListener("test", nq, nq);
      } catch (Z) {
        j7 = !1;
      }
    function yU(Z, X, $, q, H, G, E, U, P) {
      var O = Array.prototype.slice.call(arguments, 3);
      try {
        X.apply($, O);
      } catch (k) {
        this.onError(k);
      }
    }
    var fU = yU;
    if (typeof window !== "undefined" && typeof window.dispatchEvent === "function" && typeof document !== "undefined" && typeof document.createEvent === "function") {
      var B7 = document.createElement("react");
      fU = function Z(X, $, q, H, G, E, U, P, O) {
        if (typeof document === "undefined" || document === null)
          throw new Error("The `document` global was defined when React was initialized, but is not defined anymore. This can happen in a test environment if a component schedules an update from an asynchronous callback, but the test has already finished running. To solve this, you can either unmount the component at the end of your test (and ensure that any asynchronous operations get canceled in `componentWillUnmount`), or you can change the test itself to be asynchronous.");
        var k = document.createEvent("Event"), C = !1, B = !0, v = window.event, h = Object.getOwnPropertyDescriptor(window, "event");
        function f() {
          if (B7.removeEventListener(b, k0, !1), typeof window.event !== "undefined" && window.hasOwnProperty("event"))
            window.event = v;
        }
        var q0 = Array.prototype.slice.call(arguments, 3);
        function k0() {
          C = !0, f(), $.apply(q, q0), B = !1;
        }
        var w0, N1 = !1, E1 = !1;
        function _(T) {
          if (w0 = T.error, N1 = !0, w0 === null && T.colno === 0 && T.lineno === 0)
            E1 = !0;
          if (T.defaultPrevented) {
            if (w0 != null && typeof w0 === "object")
              try {
                w0._suppressLogging = !0;
              } catch (a) {}
          }
        }
        var b = "react-" + (X ? X : "invokeguardedcallback");
        if (window.addEventListener("error", _), B7.addEventListener(b, k0, !1), k.initEvent(b, !1, !1), B7.dispatchEvent(k), h)
          Object.defineProperty(window, "event", h);
        if (C && B) {
          if (!N1)
            w0 = new Error(`An error was thrown inside one of your components, but React doesn't know what it was. This is likely due to browser flakiness. React does its best to preserve the "Pause on exceptions" behavior of the DevTools, which requires some DEV-mode only tricks. It's possible that these don't work in your browser. Try triggering the error in production mode, or switching to a modern browser. If you suspect that this is actually an issue with React, please file an issue.`);
          else if (E1)
            w0 = new Error("A cross-origin error was thrown. React doesn't have access to the actual error object in development. See https://reactjs.org/link/crossorigin-error for more information.");
          this.onError(w0);
        }
        if (window.removeEventListener("error", _), !C)
          return f(), yU.apply(this, arguments);
      };
    }
    var dj = fU, YY = !1, SK = null, IK = !1, C7 = null, lj = {
      onError: function(Z) {
        YY = !0, SK = Z;
      }
    };
    function V7(Z, X, $, q, H, G, E, U, P) {
      YY = !1, SK = null, dj.apply(lj, arguments);
    }
    function nj(Z, X, $, q, H, G, E, U, P) {
      if (V7.apply(this, arguments), YY) {
        var O = S7();
        if (!IK)
          IK = !0, C7 = O;
      }
    }
    function sj() {
      if (IK) {
        var Z = C7;
        throw IK = !1, C7 = null, Z;
      }
    }
    function oj() {
      return YY;
    }
    function S7() {
      if (YY) {
        var Z = SK;
        return YY = !1, SK = null, Z;
      } else
        throw new Error("clearCaughtError was called but no error was captured. This error is likely caused by a bug in React. Please file an issue.");
    }
    function qY(Z) {
      return Z._reactInternals;
    }
    function aj(Z) {
      return Z._reactInternals !== void 0;
    }
    function rj(Z, X) {
      Z._reactInternals = X;
    }
    var S0 = 0, WY = 1, m6 = 2, O1 = 4, sJ = 16, sq = 32, I7 = 64, I1 = 128, eX = 256, f4 = 512, oJ = 1024, uZ = 2048, Q4 = 4096, aJ = 8192, _K = 16384, ij = uZ | O1 | I7 | f4 | oJ | _K, tj = 32767, oq = 32768, NQ = 65536, _7 = 131072, mU = 1048576, T7 = 2097152, rJ = 4194304, g7 = 8388608, Z4 = 16777216, TK = 33554432, x7 = O1 | oJ | 0, v7 = m6 | O1 | sJ | sq | f4 | Q4 | aJ, aq = O1 | I7 | f4 | aJ, KY = uZ | sJ, X4 = rJ | g7 | T7, ej = Q.ReactCurrentOwner;
    function iJ(Z) {
      var X = Z, $ = Z;
      if (!Z.alternate) {
        var q = X;
        do {
          if (X = q, (X.flags & (m6 | Q4)) !== S0)
            $ = X.return;
          q = X.return;
        } while (q);
      } else
        while (X.return)
          X = X.return;
      if (X.tag === w)
        return $;
      return null;
    }
    function bU(Z) {
      if (Z.tag === l) {
        var X = Z.memoizedState;
        if (X === null) {
          var $ = Z.alternate;
          if ($ !== null)
            X = $.memoizedState;
        }
        if (X !== null)
          return X.dehydrated;
      }
      return null;
    }
    function uU(Z) {
      return Z.tag === w ? Z.stateNode.containerInfo : null;
    }
    function QB(Z) {
      return iJ(Z) === Z;
    }
    function ZB(Z) {
      {
        var X = ej.current;
        if (X !== null && X.tag === F) {
          var $ = X, q = $.stateNode;
          if (!q._warnedAboutRefsInRender)
            K("%s is accessing isMounted inside its render() function. render() should be a pure function of props and state. It should never access something that requires stale data from the previous render, such as refs. Move this logic to componentDidMount and componentDidUpdate instead.", V0($) || "A component");
          q._warnedAboutRefsInRender = !0;
        }
      }
      var H = qY(Z);
      if (!H)
        return !1;
      return iJ(H) === H;
    }
    function cU(Z) {
      if (iJ(Z) !== Z)
        throw new Error("Unable to find node on an unmounted component.");
    }
    function pU(Z) {
      var X = Z.alternate;
      if (!X) {
        var $ = iJ(Z);
        if ($ === null)
          throw new Error("Unable to find node on an unmounted component.");
        if ($ !== Z)
          return null;
        return Z;
      }
      var q = Z, H = X;
      while (!0) {
        var G = q.return;
        if (G === null)
          break;
        var E = G.alternate;
        if (E === null) {
          var U = G.return;
          if (U !== null) {
            q = H = U;
            continue;
          }
          break;
        }
        if (G.child === E.child) {
          var P = G.child;
          while (P) {
            if (P === q)
              return cU(G), Z;
            if (P === H)
              return cU(G), X;
            P = P.sibling;
          }
          throw new Error("Unable to find node on an unmounted component.");
        }
        if (q.return !== H.return)
          q = G, H = E;
        else {
          var O = !1, k = G.child;
          while (k) {
            if (k === q) {
              O = !0, q = G, H = E;
              break;
            }
            if (k === H) {
              O = !0, H = G, q = E;
              break;
            }
            k = k.sibling;
          }
          if (!O) {
            k = E.child;
            while (k) {
              if (k === q) {
                O = !0, q = E, H = G;
                break;
              }
              if (k === H) {
                O = !0, H = E, q = G;
                break;
              }
              k = k.sibling;
            }
            if (!O)
              throw new Error("Child was not found in either parent set. This indicates a bug in React related to the return pointer. Please file an issue.");
          }
        }
        if (q.alternate !== H)
          throw new Error("Return fibers should always be each others' alternates. This error is likely caused by a bug in React. Please file an issue.");
      }
      if (q.tag !== w)
        throw new Error("Unable to find node on an unmounted component.");
      if (q.stateNode.current === q)
        return Z;
      return X;
    }
    function dU(Z) {
      var X = pU(Z);
      return X !== null ? lU(X) : null;
    }
    function lU(Z) {
      if (Z.tag === R || Z.tag === V)
        return Z;
      var X = Z.child;
      while (X !== null) {
        var $ = lU(X);
        if ($ !== null)
          return $;
        X = X.sibling;
      }
      return null;
    }
    function XB(Z) {
      var X = pU(Z);
      return X !== null ? nU(X) : null;
    }
    function nU(Z) {
      if (Z.tag === R || Z.tag === V)
        return Z;
      var X = Z.child;
      while (X !== null) {
        if (X.tag !== D) {
          var $ = nU(X);
          if ($ !== null)
            return $;
        }
        X = X.sibling;
      }
      return null;
    }
    var sU = p1.unstable_scheduleCallback, JB = p1.unstable_cancelCallback, $B = p1.unstable_shouldYield, YB = p1.unstable_requestPaint, E8 = p1.unstable_now, qB = p1.unstable_getCurrentPriorityLevel, gK = p1.unstable_ImmediatePriority, h7 = p1.unstable_UserBlockingPriority, tJ = p1.unstable_NormalPriority, WB = p1.unstable_LowPriority, y7 = p1.unstable_IdlePriority, KB = p1.unstable_yieldValue, HB = p1.unstable_setDisableYieldValue, eJ = null, C8 = null, G0 = null, kX = !1, cZ = typeof __REACT_DEVTOOLS_GLOBAL_HOOK__ !== "undefined";
    function GB(Z) {
      if (typeof __REACT_DEVTOOLS_GLOBAL_HOOK__ === "undefined")
        return !1;
      var X = __REACT_DEVTOOLS_GLOBAL_HOOK__;
      if (X.isDisabled)
        return !0;
      if (!X.supportsFiber)
        return K("The installed version of React DevTools is too old and will not work with the current version of React. Please update React DevTools. https://reactjs.org/link/react-devtools"), !0;
      try {
        if (x0)
          Z = K1({}, Z, {
            getLaneLabelMap: PB,
            injectProfilingHooks: UB
          });
        eJ = X.inject(Z), C8 = X;
      } catch ($) {
        K("React instrumentation encountered an error: %s.", $);
      }
      if (X.checkDCE)
        return !0;
      else
        return !1;
    }
    function zB(Z, X) {
      if (C8 && typeof C8.onScheduleFiberRoot === "function")
        try {
          C8.onScheduleFiberRoot(eJ, Z, X);
        } catch ($) {
          if (!kX)
            kX = !0, K("React instrumentation encountered an error: %s", $);
        }
    }
    function NB(Z, X) {
      if (C8 && typeof C8.onCommitFiberRoot === "function")
        try {
          var $ = (Z.current.flags & I1) === I1;
          if (N6) {
            var q;
            switch (X) {
              case sQ:
                q = gK;
                break;
              case $4:
                q = h7;
                break;
              case Y4:
                q = tJ;
                break;
              case uK:
                q = y7;
                break;
              default:
                q = tJ;
                break;
            }
            C8.onCommitFiberRoot(eJ, Z, q, $);
          } else
            C8.onCommitFiberRoot(eJ, Z, void 0, $);
        } catch (H) {
          if (!kX)
            kX = !0, K("React instrumentation encountered an error: %s", H);
        }
    }
    function EB(Z) {
      if (C8 && typeof C8.onPostCommitFiberRoot === "function")
        try {
          C8.onPostCommitFiberRoot(eJ, Z);
        } catch (X) {
          if (!kX)
            kX = !0, K("React instrumentation encountered an error: %s", X);
        }
    }
    function FB(Z) {
      if (C8 && typeof C8.onCommitFiberUnmount === "function")
        try {
          C8.onCommitFiberUnmount(eJ, Z);
        } catch (X) {
          if (!kX)
            kX = !0, K("React instrumentation encountered an error: %s", X);
        }
    }
    function F8(Z) {
      {
        if (typeof KB === "function")
          HB(Z), Y(Z);
        if (C8 && typeof C8.setStrictMode === "function")
          try {
            C8.setStrictMode(eJ, Z);
          } catch (X) {
            if (!kX)
              kX = !0, K("React instrumentation encountered an error: %s", X);
          }
      }
    }
    function UB(Z) {
      G0 = Z;
    }
    function PB() {
      {
        var Z = /* @__PURE__ */ new Map, X = 1;
        for (var $ = 0;$ < m7; $++) {
          var q = hB(X);
          Z.set(X, q), X *= 2;
        }
        return Z;
      }
    }
    function AB(Z) {
      if (G0 !== null && typeof G0.markCommitStarted === "function")
        G0.markCommitStarted(Z);
    }
    function oU() {
      if (G0 !== null && typeof G0.markCommitStopped === "function")
        G0.markCommitStopped();
    }
    function rq(Z) {
      if (G0 !== null && typeof G0.markComponentRenderStarted === "function")
        G0.markComponentRenderStarted(Z);
    }
    function HY() {
      if (G0 !== null && typeof G0.markComponentRenderStopped === "function")
        G0.markComponentRenderStopped();
    }
    function LB(Z) {
      if (G0 !== null && typeof G0.markComponentPassiveEffectMountStarted === "function")
        G0.markComponentPassiveEffectMountStarted(Z);
    }
    function OB() {
      if (G0 !== null && typeof G0.markComponentPassiveEffectMountStopped === "function")
        G0.markComponentPassiveEffectMountStopped();
    }
    function wB(Z) {
      if (G0 !== null && typeof G0.markComponentPassiveEffectUnmountStarted === "function")
        G0.markComponentPassiveEffectUnmountStarted(Z);
    }
    function MB() {
      if (G0 !== null && typeof G0.markComponentPassiveEffectUnmountStopped === "function")
        G0.markComponentPassiveEffectUnmountStopped();
    }
    function DB(Z) {
      if (G0 !== null && typeof G0.markComponentLayoutEffectMountStarted === "function")
        G0.markComponentLayoutEffectMountStarted(Z);
    }
    function kB() {
      if (G0 !== null && typeof G0.markComponentLayoutEffectMountStopped === "function")
        G0.markComponentLayoutEffectMountStopped();
    }
    function aU(Z) {
      if (G0 !== null && typeof G0.markComponentLayoutEffectUnmountStarted === "function")
        G0.markComponentLayoutEffectUnmountStarted(Z);
    }
    function rU() {
      if (G0 !== null && typeof G0.markComponentLayoutEffectUnmountStopped === "function")
        G0.markComponentLayoutEffectUnmountStopped();
    }
    function RB(Z, X, $) {
      if (G0 !== null && typeof G0.markComponentErrored === "function")
        G0.markComponentErrored(Z, X, $);
    }
    function jB(Z, X, $) {
      if (G0 !== null && typeof G0.markComponentSuspended === "function")
        G0.markComponentSuspended(Z, X, $);
    }
    function BB(Z) {
      if (G0 !== null && typeof G0.markLayoutEffectsStarted === "function")
        G0.markLayoutEffectsStarted(Z);
    }
    function CB() {
      if (G0 !== null && typeof G0.markLayoutEffectsStopped === "function")
        G0.markLayoutEffectsStopped();
    }
    function VB(Z) {
      if (G0 !== null && typeof G0.markPassiveEffectsStarted === "function")
        G0.markPassiveEffectsStarted(Z);
    }
    function SB() {
      if (G0 !== null && typeof G0.markPassiveEffectsStopped === "function")
        G0.markPassiveEffectsStopped();
    }
    function iU(Z) {
      if (G0 !== null && typeof G0.markRenderStarted === "function")
        G0.markRenderStarted(Z);
    }
    function IB() {
      if (G0 !== null && typeof G0.markRenderYielded === "function")
        G0.markRenderYielded();
    }
    function tU() {
      if (G0 !== null && typeof G0.markRenderStopped === "function")
        G0.markRenderStopped();
    }
    function _B(Z) {
      if (G0 !== null && typeof G0.markRenderScheduled === "function")
        G0.markRenderScheduled(Z);
    }
    function TB(Z, X) {
      if (G0 !== null && typeof G0.markForceUpdateScheduled === "function")
        G0.markForceUpdateScheduled(Z, X);
    }
    function f7(Z, X) {
      if (G0 !== null && typeof G0.markStateUpdateScheduled === "function")
        G0.markStateUpdateScheduled(Z, X);
    }
    var B0 = 0, A1 = 1, b1 = 2, j6 = 8, RX = 16, eU = Math.clz32 ? Math.clz32 : vB, gB = Math.log, xB = Math.LN2;
    function vB(Z) {
      var X = Z >>> 0;
      if (X === 0)
        return 32;
      return 31 - (gB(X) / xB | 0) | 0;
    }
    var m7 = 31, n = 0, U8 = 0, b0 = 1, GY = 2, J4 = 4, Q$ = 8, jX = 16, iq = 32, zY = 4194240, tq = 64, b7 = 128, u7 = 256, c7 = 512, p7 = 1024, d7 = 2048, l7 = 4096, n7 = 8192, s7 = 16384, o7 = 32768, a7 = 65536, r7 = 131072, i7 = 262144, t7 = 524288, e7 = 1048576, QG = 2097152, xK = 130023424, NY = 4194304, ZG = 8388608, XG = 16777216, JG = 33554432, $G = 67108864, QP = NY, eq = 134217728, ZP = 268435455, QW = 268435456, Z$ = 536870912, lQ = 1073741824;
    function hB(Z) {
      {
        if (Z & b0)
          return "Sync";
        if (Z & GY)
          return "InputContinuousHydration";
        if (Z & J4)
          return "InputContinuous";
        if (Z & Q$)
          return "DefaultHydration";
        if (Z & jX)
          return "Default";
        if (Z & iq)
          return "TransitionHydration";
        if (Z & zY)
          return "Transition";
        if (Z & xK)
          return "Retry";
        if (Z & eq)
          return "SelectiveHydration";
        if (Z & QW)
          return "IdleHydration";
        if (Z & Z$)
          return "Idle";
        if (Z & lQ)
          return "Offscreen";
      }
    }
    var J6 = -1, vK = tq, hK = NY;
    function ZW(Z) {
      switch (X$(Z)) {
        case b0:
          return b0;
        case GY:
          return GY;
        case J4:
          return J4;
        case Q$:
          return Q$;
        case jX:
          return jX;
        case iq:
          return iq;
        case tq:
        case b7:
        case u7:
        case c7:
        case p7:
        case d7:
        case l7:
        case n7:
        case s7:
        case o7:
        case a7:
        case r7:
        case i7:
        case t7:
        case e7:
        case QG:
          return Z & zY;
        case NY:
        case ZG:
        case XG:
        case JG:
        case $G:
          return Z & xK;
        case eq:
          return eq;
        case QW:
          return QW;
        case Z$:
          return Z$;
        case lQ:
          return lQ;
        default:
          return K("Should have found matching lanes. This is a bug in React."), Z;
      }
    }
    function yK(Z, X) {
      var $ = Z.pendingLanes;
      if ($ === n)
        return n;
      var q = n, H = Z.suspendedLanes, G = Z.pingedLanes, E = $ & ZP;
      if (E !== n) {
        var U = E & ~H;
        if (U !== n)
          q = ZW(U);
        else {
          var P = E & G;
          if (P !== n)
            q = ZW(P);
        }
      } else {
        var O = $ & ~H;
        if (O !== n)
          q = ZW(O);
        else if (G !== n)
          q = ZW(G);
      }
      if (q === n)
        return n;
      if (X !== n && X !== q && (X & H) === n) {
        var k = X$(q), C = X$(X);
        if (k >= C || k === jX && (C & zY) !== n)
          return X;
      }
      if ((q & J4) !== n)
        q |= $ & jX;
      var B = Z.entangledLanes;
      if (B !== n) {
        var v = Z.entanglements, h = q & B;
        while (h > 0) {
          var f = J$(h), q0 = 1 << f;
          q |= v[f], h &= ~q0;
        }
      }
      return q;
    }
    function yB(Z, X) {
      var $ = Z.eventTimes, q = J6;
      while (X > 0) {
        var H = J$(X), G = 1 << H, E = $[H];
        if (E > q)
          q = E;
        X &= ~G;
      }
      return q;
    }
    function fB(Z, X) {
      switch (Z) {
        case b0:
        case GY:
        case J4:
          return X + 250;
        case Q$:
        case jX:
        case iq:
        case tq:
        case b7:
        case u7:
        case c7:
        case p7:
        case d7:
        case l7:
        case n7:
        case s7:
        case o7:
        case a7:
        case r7:
        case i7:
        case t7:
        case e7:
        case QG:
          return X + 5000;
        case NY:
        case ZG:
        case XG:
        case JG:
        case $G:
          return J6;
        case eq:
        case QW:
        case Z$:
        case lQ:
          return J6;
        default:
          return K("Should have found matching lanes. This is a bug in React."), J6;
      }
    }
    function mB(Z, X) {
      var { pendingLanes: $, suspendedLanes: q, pingedLanes: H, expirationTimes: G } = Z, E = $;
      while (E > 0) {
        var U = J$(E), P = 1 << U, O = G[U];
        if (O === J6) {
          if ((P & q) === n || (P & H) !== n)
            G[U] = fB(P, X);
        } else if (O <= X)
          Z.expiredLanes |= P;
        E &= ~P;
      }
    }
    function bB(Z) {
      return ZW(Z.pendingLanes);
    }
    function YG(Z) {
      var X = Z.pendingLanes & ~lQ;
      if (X !== n)
        return X;
      if (X & lQ)
        return lQ;
      return n;
    }
    function uB(Z) {
      return (Z & b0) !== n;
    }
    function qG(Z) {
      return (Z & ZP) !== n;
    }
    function XP(Z) {
      return (Z & xK) === Z;
    }
    function cB(Z) {
      var X = b0 | J4 | jX;
      return (Z & X) === n;
    }
    function pB(Z) {
      return (Z & zY) === Z;
    }
    function fK(Z, X) {
      var $ = GY | J4 | Q$ | jX;
      return (X & $) !== n;
    }
    function dB(Z, X) {
      return (X & Z.expiredLanes) !== n;
    }
    function JP(Z) {
      return (Z & zY) !== n;
    }
    function $P() {
      var Z = vK;
      if (vK <<= 1, (vK & zY) === n)
        vK = tq;
      return Z;
    }
    function lB() {
      var Z = hK;
      if (hK <<= 1, (hK & xK) === n)
        hK = NY;
      return Z;
    }
    function X$(Z) {
      return Z & -Z;
    }
    function XW(Z) {
      return X$(Z);
    }
    function J$(Z) {
      return 31 - eU(Z);
    }
    function WG(Z) {
      return J$(Z);
    }
    function nQ(Z, X) {
      return (Z & X) !== n;
    }
    function EY(Z, X) {
      return (Z & X) === X;
    }
    function Q1(Z, X) {
      return Z | X;
    }
    function mK(Z, X) {
      return Z & ~X;
    }
    function YP(Z, X) {
      return Z & X;
    }
    function bK(Z) {
      return Z;
    }
    function nB(Z, X) {
      return Z !== U8 && Z < X ? Z : X;
    }
    function KG(Z) {
      var X = [];
      for (var $ = 0;$ < m7; $++)
        X.push(Z);
      return X;
    }
    function JW(Z, X, $) {
      if (Z.pendingLanes |= X, X !== Z$)
        Z.suspendedLanes = n, Z.pingedLanes = n;
      var q = Z.eventTimes, H = WG(X);
      q[H] = $;
    }
    function sB(Z, X) {
      Z.suspendedLanes |= X, Z.pingedLanes &= ~X;
      var $ = Z.expirationTimes, q = X;
      while (q > 0) {
        var H = J$(q), G = 1 << H;
        $[H] = J6, q &= ~G;
      }
    }
    function qP(Z, X, $) {
      Z.pingedLanes |= Z.suspendedLanes & X;
    }
    function oB(Z, X) {
      var $ = Z.pendingLanes & ~X;
      Z.pendingLanes = X, Z.suspendedLanes = n, Z.pingedLanes = n, Z.expiredLanes &= X, Z.mutableReadLanes &= X, Z.entangledLanes &= X;
      var { entanglements: q, eventTimes: H, expirationTimes: G } = Z, E = $;
      while (E > 0) {
        var U = J$(E), P = 1 << U;
        q[U] = n, H[U] = J6, G[U] = J6, E &= ~P;
      }
    }
    function HG(Z, X) {
      var $ = Z.entangledLanes |= X, q = Z.entanglements, H = $;
      while (H) {
        var G = J$(H), E = 1 << G;
        if (E & X | q[G] & X)
          q[G] |= X;
        H &= ~E;
      }
    }
    function aB(Z, X) {
      var $ = X$(X), q;
      switch ($) {
        case J4:
          q = GY;
          break;
        case jX:
          q = Q$;
          break;
        case tq:
        case b7:
        case u7:
        case c7:
        case p7:
        case d7:
        case l7:
        case n7:
        case s7:
        case o7:
        case a7:
        case r7:
        case i7:
        case t7:
        case e7:
        case QG:
        case NY:
        case ZG:
        case XG:
        case JG:
        case $G:
          q = iq;
          break;
        case Z$:
          q = QW;
          break;
        default:
          q = U8;
          break;
      }
      if ((q & (Z.suspendedLanes | X)) !== U8)
        return U8;
      return q;
    }
    function WP(Z, X, $) {
      if (!cZ)
        return;
      var q = Z.pendingUpdatersLaneMap;
      while ($ > 0) {
        var H = WG($), G = 1 << H, E = q[H];
        E.add(X), $ &= ~G;
      }
    }
    function KP(Z, X) {
      if (!cZ)
        return;
      var { pendingUpdatersLaneMap: $, memoizedUpdaters: q } = Z;
      while (X > 0) {
        var H = WG(X), G = 1 << H, E = $[H];
        if (E.size > 0)
          E.forEach(function(U) {
            var P = U.alternate;
            if (P === null || !q.has(P))
              q.add(U);
          }), E.clear();
        X &= ~G;
      }
    }
    function HP(Z, X) {
      return null;
    }
    var sQ = b0, $4 = J4, Y4 = jX, uK = Z$, $W = U8;
    function pZ() {
      return $W;
    }
    function P8(Z) {
      $W = Z;
    }
    function rB(Z, X) {
      var $ = $W;
      try {
        return $W = Z, X();
      } finally {
        $W = $;
      }
    }
    function iB(Z, X) {
      return Z !== 0 && Z < X ? Z : X;
    }
    function tB(Z, X) {
      return Z === 0 || Z > X ? Z : X;
    }
    function GG(Z, X) {
      return Z !== 0 && Z < X;
    }
    function GP(Z) {
      var X = X$(Z);
      if (!GG(sQ, X))
        return sQ;
      if (!GG($4, X))
        return $4;
      if (qG(X))
        return Y4;
      return uK;
    }
    function cK(Z) {
      var X = Z.current.memoizedState;
      return X.isDehydrated;
    }
    var zP;
    function eB(Z) {
      zP = Z;
    }
    function QC(Z) {
      zP(Z);
    }
    var zG;
    function ZC(Z) {
      zG = Z;
    }
    var NP;
    function XC(Z) {
      NP = Z;
    }
    var EP;
    function JC(Z) {
      EP = Z;
    }
    var FP;
    function $C(Z) {
      FP = Z;
    }
    var NG = !1, pK = [], m4 = null, b4 = null, u4 = null, YW = /* @__PURE__ */ new Map, qW = /* @__PURE__ */ new Map, c4 = [], YC = [
      "mousedown",
      "mouseup",
      "touchcancel",
      "touchend",
      "touchstart",
      "auxclick",
      "dblclick",
      "pointercancel",
      "pointerdown",
      "pointerup",
      "dragend",
      "dragstart",
      "drop",
      "compositionend",
      "compositionstart",
      "keydown",
      "keypress",
      "keyup",
      "input",
      "textInput",
      "copy",
      "cut",
      "paste",
      "click",
      "change",
      "contextmenu",
      "reset",
      "submit"
    ];
    function qC(Z) {
      return YC.indexOf(Z) > -1;
    }
    function WC(Z, X, $, q, H) {
      return {
        blockedOn: Z,
        domEventName: X,
        eventSystemFlags: $,
        nativeEvent: H,
        targetContainers: [q]
      };
    }
    function UP(Z, X) {
      switch (Z) {
        case "focusin":
        case "focusout":
          m4 = null;
          break;
        case "dragenter":
        case "dragleave":
          b4 = null;
          break;
        case "mouseover":
        case "mouseout":
          u4 = null;
          break;
        case "pointerover":
        case "pointerout": {
          var $ = X.pointerId;
          YW.delete($);
          break;
        }
        case "gotpointercapture":
        case "lostpointercapture": {
          var q = X.pointerId;
          qW.delete(q);
          break;
        }
      }
    }
    function WW(Z, X, $, q, H, G) {
      if (Z === null || Z.nativeEvent !== G) {
        var E = WC(X, $, q, H, G);
        if (X !== null) {
          var U = l4(X);
          if (U !== null)
            zG(U);
        }
        return E;
      }
      Z.eventSystemFlags |= q;
      var P = Z.targetContainers;
      if (H !== null && P.indexOf(H) === -1)
        P.push(H);
      return Z;
    }
    function KC(Z, X, $, q, H) {
      switch (X) {
        case "focusin": {
          var G = H;
          return m4 = WW(m4, Z, X, $, q, G), !0;
        }
        case "dragenter": {
          var E = H;
          return b4 = WW(b4, Z, X, $, q, E), !0;
        }
        case "mouseover": {
          var U = H;
          return u4 = WW(u4, Z, X, $, q, U), !0;
        }
        case "pointerover": {
          var P = H, O = P.pointerId;
          return YW.set(O, WW(YW.get(O) || null, Z, X, $, q, P)), !0;
        }
        case "gotpointercapture": {
          var k = H, C = k.pointerId;
          return qW.set(C, WW(qW.get(C) || null, Z, X, $, q, k)), !0;
        }
      }
      return !1;
    }
    function PP(Z) {
      var X = q$(Z.target);
      if (X !== null) {
        var $ = iJ(X);
        if ($ !== null) {
          var q = $.tag;
          if (q === l) {
            var H = bU($);
            if (H !== null) {
              Z.blockedOn = H, FP(Z.priority, function() {
                NP($);
              });
              return;
            }
          } else if (q === w) {
            var G = $.stateNode;
            if (cK(G)) {
              Z.blockedOn = uU($);
              return;
            }
          }
        }
      }
      Z.blockedOn = null;
    }
    function HC(Z) {
      var X = EP(), $ = {
        blockedOn: null,
        target: Z,
        priority: X
      }, q = 0;
      for (;q < c4.length; q++)
        if (!GG(X, c4[q].priority))
          break;
      if (c4.splice(q, 0, $), q === 0)
        PP($);
    }
    function dK(Z) {
      if (Z.blockedOn !== null)
        return !1;
      var X = Z.targetContainers;
      while (X.length > 0) {
        var $ = X[0], q = UG(Z.domEventName, Z.eventSystemFlags, $, Z.nativeEvent);
        if (q === null) {
          var H = Z.nativeEvent, G = new H.constructor(H.type, H);
          vj(G), H.target.dispatchEvent(G), hj();
        } else {
          var E = l4(q);
          if (E !== null)
            zG(E);
          return Z.blockedOn = q, !1;
        }
        X.shift();
      }
      return !0;
    }
    function AP(Z, X, $) {
      if (dK(Z))
        $.delete(X);
    }
    function GC() {
      if (NG = !1, m4 !== null && dK(m4))
        m4 = null;
      if (b4 !== null && dK(b4))
        b4 = null;
      if (u4 !== null && dK(u4))
        u4 = null;
      YW.forEach(AP), qW.forEach(AP);
    }
    function KW(Z, X) {
      if (Z.blockedOn === X) {
        if (Z.blockedOn = null, !NG)
          NG = !0, p1.unstable_scheduleCallback(p1.unstable_NormalPriority, GC);
      }
    }
    function HW(Z) {
      if (pK.length > 0) {
        KW(pK[0], Z);
        for (var X = 1;X < pK.length; X++) {
          var $ = pK[X];
          if ($.blockedOn === Z)
            $.blockedOn = null;
        }
      }
      if (m4 !== null)
        KW(m4, Z);
      if (b4 !== null)
        KW(b4, Z);
      if (u4 !== null)
        KW(u4, Z);
      var q = function(U) {
        return KW(U, Z);
      };
      YW.forEach(q), qW.forEach(q);
      for (var H = 0;H < c4.length; H++) {
        var G = c4[H];
        if (G.blockedOn === Z)
          G.blockedOn = null;
      }
      while (c4.length > 0) {
        var E = c4[0];
        if (E.blockedOn !== null)
          break;
        else if (PP(E), E.blockedOn === null)
          c4.shift();
      }
    }
    var FY = Q.ReactCurrentBatchConfig, EG = !0;
    function LP(Z) {
      EG = !!Z;
    }
    function zC() {
      return EG;
    }
    function NC(Z, X, $) {
      var q = OP(X), H;
      switch (q) {
        case sQ:
          H = EC;
          break;
        case $4:
          H = FC;
          break;
        case Y4:
        default:
          H = FG;
          break;
      }
      return H.bind(null, X, $, Z);
    }
    function EC(Z, X, $, q) {
      var H = pZ(), G = FY.transition;
      FY.transition = null;
      try {
        P8(sQ), FG(Z, X, $, q);
      } finally {
        P8(H), FY.transition = G;
      }
    }
    function FC(Z, X, $, q) {
      var H = pZ(), G = FY.transition;
      FY.transition = null;
      try {
        P8($4), FG(Z, X, $, q);
      } finally {
        P8(H), FY.transition = G;
      }
    }
    function FG(Z, X, $, q) {
      if (!EG)
        return;
      UC(Z, X, $, q);
    }
    function UC(Z, X, $, q) {
      var H = UG(Z, X, $, q);
      if (H === null) {
        SG(Z, X, q, lK, $), UP(Z, q);
        return;
      }
      if (KC(H, Z, X, $, q)) {
        q.stopPropagation();
        return;
      }
      if (UP(Z, q), X & pq && qC(Z)) {
        while (H !== null) {
          var G = l4(H);
          if (G !== null)
            QC(G);
          var E = UG(Z, X, $, q);
          if (E === null)
            SG(Z, X, q, lK, $);
          if (E === H)
            break;
          H = E;
        }
        if (H !== null)
          q.stopPropagation();
        return;
      }
      SG(Z, X, q, null, $);
    }
    var lK = null;
    function UG(Z, X, $, q) {
      lK = null;
      var H = D7(q), G = q$(H);
      if (G !== null) {
        var E = iJ(G);
        if (E === null)
          G = null;
        else {
          var U = E.tag;
          if (U === l) {
            var P = bU(E);
            if (P !== null)
              return P;
            G = null;
          } else if (U === w) {
            var O = E.stateNode;
            if (cK(O))
              return uU(E);
            G = null;
          } else if (E !== G)
            G = null;
        }
      }
      return lK = G, null;
    }
    function OP(Z) {
      switch (Z) {
        case "cancel":
        case "click":
        case "close":
        case "contextmenu":
        case "copy":
        case "cut":
        case "auxclick":
        case "dblclick":
        case "dragend":
        case "dragstart":
        case "drop":
        case "focusin":
        case "focusout":
        case "input":
        case "invalid":
        case "keydown":
        case "keypress":
        case "keyup":
        case "mousedown":
        case "mouseup":
        case "paste":
        case "pause":
        case "play":
        case "pointercancel":
        case "pointerdown":
        case "pointerup":
        case "ratechange":
        case "reset":
        case "resize":
        case "seeked":
        case "submit":
        case "touchcancel":
        case "touchend":
        case "touchstart":
        case "volumechange":
        case "change":
        case "selectionchange":
        case "textInput":
        case "compositionstart":
        case "compositionend":
        case "compositionupdate":
        case "beforeblur":
        case "afterblur":
        case "beforeinput":
        case "blur":
        case "fullscreenchange":
        case "focus":
        case "hashchange":
        case "popstate":
        case "select":
        case "selectstart":
          return sQ;
        case "drag":
        case "dragenter":
        case "dragexit":
        case "dragleave":
        case "dragover":
        case "mousemove":
        case "mouseout":
        case "mouseover":
        case "pointermove":
        case "pointerout":
        case "pointerover":
        case "scroll":
        case "toggle":
        case "touchmove":
        case "wheel":
        case "mouseenter":
        case "mouseleave":
        case "pointerenter":
        case "pointerleave":
          return $4;
        case "message": {
          var X = qB();
          switch (X) {
            case gK:
              return sQ;
            case h7:
              return $4;
            case tJ:
            case WB:
              return Y4;
            case y7:
              return uK;
            default:
              return Y4;
          }
        }
        default:
          return Y4;
      }
    }
    function PC(Z, X, $) {
      return Z.addEventListener(X, $, !1), $;
    }
    function AC(Z, X, $) {
      return Z.addEventListener(X, $, !0), $;
    }
    function LC(Z, X, $, q) {
      return Z.addEventListener(X, $, {
        capture: !0,
        passive: q
      }), $;
    }
    function OC(Z, X, $, q) {
      return Z.addEventListener(X, $, {
        passive: q
      }), $;
    }
    var GW = null, PG = null, zW = null;
    function wC(Z) {
      return GW = Z, PG = MP(), !0;
    }
    function MC() {
      GW = null, PG = null, zW = null;
    }
    function wP() {
      if (zW)
        return zW;
      var Z, X = PG, $ = X.length, q, H = MP(), G = H.length;
      for (Z = 0;Z < $; Z++)
        if (X[Z] !== H[Z])
          break;
      var E = $ - Z;
      for (q = 1;q <= E; q++)
        if (X[$ - q] !== H[G - q])
          break;
      var U = q > 1 ? 1 - q : void 0;
      return zW = H.slice(Z, U), zW;
    }
    function MP() {
      if ("value" in GW)
        return GW.value;
      return GW.textContent;
    }
    function nK(Z) {
      var X, $ = Z.keyCode;
      if ("charCode" in Z) {
        if (X = Z.charCode, X === 0 && $ === 13)
          X = 13;
      } else
        X = $;
      if (X === 10)
        X = 13;
      if (X >= 32 || X === 13)
        return X;
      return 0;
    }
    function sK() {
      return !0;
    }
    function DP() {
      return !1;
    }
    function oQ(Z) {
      function X($, q, H, G, E) {
        this._reactName = $, this._targetInst = H, this.type = q, this.nativeEvent = G, this.target = E, this.currentTarget = null;
        for (var U in Z) {
          if (!Z.hasOwnProperty(U))
            continue;
          var P = Z[U];
          if (P)
            this[U] = P(G);
          else
            this[U] = G[U];
        }
        var O = G.defaultPrevented != null ? G.defaultPrevented : G.returnValue === !1;
        if (O)
          this.isDefaultPrevented = sK;
        else
          this.isDefaultPrevented = DP;
        return this.isPropagationStopped = DP, this;
      }
      return K1(X.prototype, {
        preventDefault: function() {
          this.defaultPrevented = !0;
          var $ = this.nativeEvent;
          if (!$)
            return;
          if ($.preventDefault)
            $.preventDefault();
          else if (typeof $.returnValue !== "unknown")
            $.returnValue = !1;
          this.isDefaultPrevented = sK;
        },
        stopPropagation: function() {
          var $ = this.nativeEvent;
          if (!$)
            return;
          if ($.stopPropagation)
            $.stopPropagation();
          else if (typeof $.cancelBubble !== "unknown")
            $.cancelBubble = !0;
          this.isPropagationStopped = sK;
        },
        persist: function() {},
        isPersistent: sK
      }), X;
    }
    var UY = {
      eventPhase: 0,
      bubbles: 0,
      cancelable: 0,
      timeStamp: function(Z) {
        return Z.timeStamp || Date.now();
      },
      defaultPrevented: 0,
      isTrusted: 0
    }, AG = oQ(UY), NW = K1({}, UY, {
      view: 0,
      detail: 0
    }), DC = oQ(NW), LG, OG, EW;
    function kC(Z) {
      if (Z !== EW) {
        if (EW && Z.type === "mousemove")
          LG = Z.screenX - EW.screenX, OG = Z.screenY - EW.screenY;
        else
          LG = 0, OG = 0;
        EW = Z;
      }
    }
    var oK = K1({}, NW, {
      screenX: 0,
      screenY: 0,
      clientX: 0,
      clientY: 0,
      pageX: 0,
      pageY: 0,
      ctrlKey: 0,
      shiftKey: 0,
      altKey: 0,
      metaKey: 0,
      getModifierState: MG,
      button: 0,
      buttons: 0,
      relatedTarget: function(Z) {
        if (Z.relatedTarget === void 0)
          return Z.fromElement === Z.srcElement ? Z.toElement : Z.fromElement;
        return Z.relatedTarget;
      },
      movementX: function(Z) {
        if ("movementX" in Z)
          return Z.movementX;
        return kC(Z), LG;
      },
      movementY: function(Z) {
        if ("movementY" in Z)
          return Z.movementY;
        return OG;
      }
    }), kP = oQ(oK), RC = K1({}, oK, {
      dataTransfer: 0
    }), jC = oQ(RC), BC = K1({}, NW, {
      relatedTarget: 0
    }), wG = oQ(BC), CC = K1({}, UY, {
      animationName: 0,
      elapsedTime: 0,
      pseudoElement: 0
    }), VC = oQ(CC), SC = K1({}, UY, {
      clipboardData: function(Z) {
        return "clipboardData" in Z ? Z.clipboardData : window.clipboardData;
      }
    }), IC = oQ(SC), _C = K1({}, UY, {
      data: 0
    }), RP = oQ(_C), TC = RP, gC = {
      Esc: "Escape",
      Spacebar: " ",
      Left: "ArrowLeft",
      Up: "ArrowUp",
      Right: "ArrowRight",
      Down: "ArrowDown",
      Del: "Delete",
      Win: "OS",
      Menu: "ContextMenu",
      Apps: "ContextMenu",
      Scroll: "ScrollLock",
      MozPrintableKey: "Unidentified"
    }, xC = {
      "8": "Backspace",
      "9": "Tab",
      "12": "Clear",
      "13": "Enter",
      "16": "Shift",
      "17": "Control",
      "18": "Alt",
      "19": "Pause",
      "20": "CapsLock",
      "27": "Escape",
      "32": " ",
      "33": "PageUp",
      "34": "PageDown",
      "35": "End",
      "36": "Home",
      "37": "ArrowLeft",
      "38": "ArrowUp",
      "39": "ArrowRight",
      "40": "ArrowDown",
      "45": "Insert",
      "46": "Delete",
      "112": "F1",
      "113": "F2",
      "114": "F3",
      "115": "F4",
      "116": "F5",
      "117": "F6",
      "118": "F7",
      "119": "F8",
      "120": "F9",
      "121": "F10",
      "122": "F11",
      "123": "F12",
      "144": "NumLock",
      "145": "ScrollLock",
      "224": "Meta"
    };
    function vC(Z) {
      if (Z.key) {
        var X = gC[Z.key] || Z.key;
        if (X !== "Unidentified")
          return X;
      }
      if (Z.type === "keypress") {
        var $ = nK(Z);
        return $ === 13 ? "Enter" : String.fromCharCode($);
      }
      if (Z.type === "keydown" || Z.type === "keyup")
        return xC[Z.keyCode] || "Unidentified";
      return "";
    }
    var hC = {
      Alt: "altKey",
      Control: "ctrlKey",
      Meta: "metaKey",
      Shift: "shiftKey"
    };
    function yC(Z) {
      var X = this, $ = X.nativeEvent;
      if ($.getModifierState)
        return $.getModifierState(Z);
      var q = hC[Z];
      return q ? !!$[q] : !1;
    }
    function MG(Z) {
      return yC;
    }
    var fC = K1({}, NW, {
      key: vC,
      code: 0,
      location: 0,
      ctrlKey: 0,
      shiftKey: 0,
      altKey: 0,
      metaKey: 0,
      repeat: 0,
      locale: 0,
      getModifierState: MG,
      charCode: function(Z) {
        if (Z.type === "keypress")
          return nK(Z);
        return 0;
      },
      keyCode: function(Z) {
        if (Z.type === "keydown" || Z.type === "keyup")
          return Z.keyCode;
        return 0;
      },
      which: function(Z) {
        if (Z.type === "keypress")
          return nK(Z);
        if (Z.type === "keydown" || Z.type === "keyup")
          return Z.keyCode;
        return 0;
      }
    }), mC = oQ(fC), bC = K1({}, oK, {
      pointerId: 0,
      width: 0,
      height: 0,
      pressure: 0,
      tangentialPressure: 0,
      tiltX: 0,
      tiltY: 0,
      twist: 0,
      pointerType: 0,
      isPrimary: 0
    }), jP = oQ(bC), uC = K1({}, NW, {
      touches: 0,
      targetTouches: 0,
      changedTouches: 0,
      altKey: 0,
      metaKey: 0,
      ctrlKey: 0,
      shiftKey: 0,
      getModifierState: MG
    }), cC = oQ(uC), pC = K1({}, UY, {
      propertyName: 0,
      elapsedTime: 0,
      pseudoElement: 0
    }), dC = oQ(pC), lC = K1({}, oK, {
      deltaX: function(Z) {
        return "deltaX" in Z ? Z.deltaX : ("wheelDeltaX" in Z) ? -Z.wheelDeltaX : 0;
      },
      deltaY: function(Z) {
        return "deltaY" in Z ? Z.deltaY : ("wheelDeltaY" in Z) ? -Z.wheelDeltaY : ("wheelDelta" in Z) ? -Z.wheelDelta : 0;
      },
      deltaZ: 0,
      deltaMode: 0
    }), nC = oQ(lC), sC = [9, 13, 27, 32], BP = 229, DG = i1 && "CompositionEvent" in window, FW = null;
    if (i1 && "documentMode" in document)
      FW = document.documentMode;
    var oC = i1 && "TextEvent" in window && !FW, CP = i1 && (!DG || FW && FW > 8 && FW <= 11), VP = 32, SP = String.fromCharCode(VP);
    function aC() {
      x1("onBeforeInput", ["compositionend", "keypress", "textInput", "paste"]), x1("onCompositionEnd", ["compositionend", "focusout", "keydown", "keypress", "keyup", "mousedown"]), x1("onCompositionStart", ["compositionstart", "focusout", "keydown", "keypress", "keyup", "mousedown"]), x1("onCompositionUpdate", ["compositionupdate", "focusout", "keydown", "keypress", "keyup", "mousedown"]);
    }
    var IP = !1;
    function rC(Z) {
      return (Z.ctrlKey || Z.altKey || Z.metaKey) && !(Z.ctrlKey && Z.altKey);
    }
    function iC(Z) {
      switch (Z) {
        case "compositionstart":
          return "onCompositionStart";
        case "compositionend":
          return "onCompositionEnd";
        case "compositionupdate":
          return "onCompositionUpdate";
      }
    }
    function tC(Z, X) {
      return Z === "keydown" && X.keyCode === BP;
    }
    function _P(Z, X) {
      switch (Z) {
        case "keyup":
          return sC.indexOf(X.keyCode) !== -1;
        case "keydown":
          return X.keyCode !== BP;
        case "keypress":
        case "mousedown":
        case "focusout":
          return !0;
        default:
          return !1;
      }
    }
    function TP(Z) {
      var X = Z.detail;
      if (typeof X === "object" && "data" in X)
        return X.data;
      return null;
    }
    function gP(Z) {
      return Z.locale === "ko";
    }
    var PY = !1;
    function eC(Z, X, $, q, H) {
      var G, E;
      if (DG)
        G = iC(X);
      else if (!PY) {
        if (tC(X, q))
          G = "onCompositionStart";
      } else if (_P(X, q))
        G = "onCompositionEnd";
      if (!G)
        return null;
      if (CP && !gP(q)) {
        if (!PY && G === "onCompositionStart")
          PY = wC(H);
        else if (G === "onCompositionEnd") {
          if (PY)
            E = wP();
        }
      }
      var U = eK($, G);
      if (U.length > 0) {
        var P = new RP(G, X, null, q, H);
        if (Z.push({
          event: P,
          listeners: U
        }), E)
          P.data = E;
        else {
          var O = TP(q);
          if (O !== null)
            P.data = O;
        }
      }
    }
    function QV(Z, X) {
      switch (Z) {
        case "compositionend":
          return TP(X);
        case "keypress":
          var $ = X.which;
          if ($ !== VP)
            return null;
          return IP = !0, SP;
        case "textInput":
          var q = X.data;
          if (q === SP && IP)
            return null;
          return q;
        default:
          return null;
      }
    }
    function ZV(Z, X) {
      if (PY) {
        if (Z === "compositionend" || !DG && _P(Z, X)) {
          var $ = wP();
          return MC(), PY = !1, $;
        }
        return null;
      }
      switch (Z) {
        case "paste":
          return null;
        case "keypress":
          if (!rC(X)) {
            if (X.char && X.char.length > 1)
              return X.char;
            else if (X.which)
              return String.fromCharCode(X.which);
          }
          return null;
        case "compositionend":
          return CP && !gP(X) ? null : X.data;
        default:
          return null;
      }
    }
    function XV(Z, X, $, q, H) {
      var G;
      if (oC)
        G = QV(X, q);
      else
        G = ZV(X, q);
      if (!G)
        return null;
      var E = eK($, "onBeforeInput");
      if (E.length > 0) {
        var U = new TC("onBeforeInput", "beforeinput", null, q, H);
        Z.push({
          event: U,
          listeners: E
        }), U.data = G;
      }
    }
    function JV(Z, X, $, q, H, G, E) {
      eC(Z, X, $, q, H), XV(Z, X, $, q, H);
    }
    var $V = {
      color: !0,
      date: !0,
      datetime: !0,
      "datetime-local": !0,
      email: !0,
      month: !0,
      number: !0,
      password: !0,
      range: !0,
      search: !0,
      tel: !0,
      text: !0,
      time: !0,
      url: !0,
      week: !0
    };
    function xP(Z) {
      var X = Z && Z.nodeName && Z.nodeName.toLowerCase();
      if (X === "input")
        return !!$V[Z.type];
      if (X === "textarea")
        return !0;
      return !1;
    }
    function YV(Z) {
      if (!i1)
        return !1;
      var X = "on" + Z, $ = X in document;
      if (!$) {
        var q = document.createElement("div");
        q.setAttribute(X, "return;"), $ = typeof q[X] === "function";
      }
      return $;
    }
    function qV() {
      x1("onChange", ["change", "click", "focusin", "focusout", "input", "keydown", "keyup", "selectionchange"]);
    }
    function vP(Z, X, $, q) {
      TU(q);
      var H = eK(X, "onChange");
      if (H.length > 0) {
        var G = new AG("onChange", "change", null, $, q);
        Z.push({
          event: G,
          listeners: H
        });
      }
    }
    var UW = null, PW = null;
    function WV(Z) {
      var X = Z.nodeName && Z.nodeName.toLowerCase();
      return X === "select" || X === "input" && Z.type === "file";
    }
    function KV(Z) {
      var X = [];
      vP(X, PW, Z, D7(Z)), hU(HV, X);
    }
    function HV(Z) {
      eP(Z, 0);
    }
    function aK(Z) {
      var X = DY(Z);
      if (t$(X))
        return Z;
    }
    function GV(Z, X) {
      if (Z === "change")
        return X;
    }
    var hP = !1;
    if (i1)
      hP = YV("input") && (!document.documentMode || document.documentMode > 9);
    function zV(Z, X) {
      UW = Z, PW = X, UW.attachEvent("onpropertychange", fP);
    }
    function yP() {
      if (!UW)
        return;
      UW.detachEvent("onpropertychange", fP), UW = null, PW = null;
    }
    function fP(Z) {
      if (Z.propertyName !== "value")
        return;
      if (aK(PW))
        KV(Z);
    }
    function NV(Z, X, $) {
      if (Z === "focusin")
        yP(), zV(X, $);
      else if (Z === "focusout")
        yP();
    }
    function EV(Z, X) {
      if (Z === "selectionchange" || Z === "keyup" || Z === "keydown")
        return aK(PW);
    }
    function FV(Z) {
      var X = Z.nodeName;
      return X && X.toLowerCase() === "input" && (Z.type === "checkbox" || Z.type === "radio");
    }
    function UV(Z, X) {
      if (Z === "click")
        return aK(X);
    }
    function PV(Z, X) {
      if (Z === "input" || Z === "change")
        return aK(X);
    }
    function AV(Z) {
      var X = Z._wrapperState;
      if (!X || !X.controlled || Z.type !== "number")
        return;
      m0(Z, "number", Z.value);
    }
    function LV(Z, X, $, q, H, G, E) {
      var U = $ ? DY($) : window, P, O;
      if (WV(U))
        P = GV;
      else if (xP(U))
        if (hP)
          P = PV;
        else
          P = EV, O = NV;
      else if (FV(U))
        P = UV;
      if (P) {
        var k = P(X, $);
        if (k) {
          vP(Z, k, q, H);
          return;
        }
      }
      if (O)
        O(X, U, $);
      if (X === "focusout")
        AV(U);
    }
    function OV() {
      l0("onMouseEnter", ["mouseout", "mouseover"]), l0("onMouseLeave", ["mouseout", "mouseover"]), l0("onPointerEnter", ["pointerout", "pointerover"]), l0("onPointerLeave", ["pointerout", "pointerover"]);
    }
    function wV(Z, X, $, q, H, G, E) {
      var U = X === "mouseover" || X === "pointerover", P = X === "mouseout" || X === "pointerout";
      if (U && !yj(q)) {
        var O = q.relatedTarget || q.fromElement;
        if (O) {
          if (q$(O) || _W(O))
            return;
        }
      }
      if (!P && !U)
        return;
      var k;
      if (H.window === H)
        k = H;
      else {
        var C = H.ownerDocument;
        if (C)
          k = C.defaultView || C.parentWindow;
        else
          k = window;
      }
      var B, v;
      if (P) {
        var h = q.relatedTarget || q.toElement;
        if (B = $, v = h ? q$(h) : null, v !== null) {
          var f = iJ(v);
          if (v !== f || v.tag !== R && v.tag !== V)
            v = null;
        }
      } else
        B = null, v = $;
      if (B === v)
        return;
      var q0 = kP, k0 = "onMouseLeave", w0 = "onMouseEnter", N1 = "mouse";
      if (X === "pointerout" || X === "pointerover")
        q0 = jP, k0 = "onPointerLeave", w0 = "onPointerEnter", N1 = "pointer";
      var E1 = B == null ? k : DY(B), _ = v == null ? k : DY(v), b = new q0(k0, N1 + "leave", B, q, H);
      b.target = E1, b.relatedTarget = _;
      var T = null, a = q$(H);
      if (a === $) {
        var E0 = new q0(w0, N1 + "enter", v, q, H);
        E0.target = _, E0.relatedTarget = E1, T = E0;
      }
      dV(Z, b, T, B, v);
    }
    function MV(Z, X) {
      return Z === X && (Z !== 0 || 1 / Z === 1 / X) || Z !== Z && X !== X;
    }
    var aQ = typeof Object.is === "function" ? Object.is : MV;
    function AW(Z, X) {
      if (aQ(Z, X))
        return !0;
      if (typeof Z !== "object" || Z === null || typeof X !== "object" || X === null)
        return !1;
      var $ = Object.keys(Z), q = Object.keys(X);
      if ($.length !== q.length)
        return !1;
      for (var H = 0;H < $.length; H++) {
        var G = $[H];
        if (!Z0.call(X, G) || !aQ(Z[G], X[G]))
          return !1;
      }
      return !0;
    }
    function mP(Z) {
      while (Z && Z.firstChild)
        Z = Z.firstChild;
      return Z;
    }
    function DV(Z) {
      while (Z) {
        if (Z.nextSibling)
          return Z.nextSibling;
        Z = Z.parentNode;
      }
    }
    function bP(Z, X) {
      var $ = mP(Z), q = 0, H = 0;
      while ($) {
        if ($.nodeType === iX) {
          if (H = q + $.textContent.length, q <= X && H >= X)
            return {
              node: $,
              offset: X - q
            };
          q = H;
        }
        $ = mP(DV($));
      }
    }
    function kV(Z) {
      var X = Z.ownerDocument, $ = X && X.defaultView || window, q = $.getSelection && $.getSelection();
      if (!q || q.rangeCount === 0)
        return null;
      var { anchorNode: H, anchorOffset: G, focusNode: E, focusOffset: U } = q;
      try {
        H.nodeType, E.nodeType;
      } catch (P) {
        return null;
      }
      return RV(Z, H, G, E, U);
    }
    function RV(Z, X, $, q, H) {
      var G = 0, E = -1, U = -1, P = 0, O = 0, k = Z, C = null;
      Q:
        while (!0) {
          var B = null;
          while (!0) {
            if (k === X && ($ === 0 || k.nodeType === iX))
              E = G + $;
            if (k === q && (H === 0 || k.nodeType === iX))
              U = G + H;
            if (k.nodeType === iX)
              G += k.nodeValue.length;
            if ((B = k.firstChild) === null)
              break;
            C = k, k = B;
          }
          while (!0) {
            if (k === Z)
              break Q;
            if (C === X && ++P === $)
              E = G;
            if (C === q && ++O === H)
              U = G;
            if ((B = k.nextSibling) !== null)
              break;
            k = C, C = k.parentNode;
          }
          k = B;
        }
      if (E === -1 || U === -1)
        return null;
      return {
        start: E,
        end: U
      };
    }
    function jV(Z, X) {
      var $ = Z.ownerDocument || document, q = $ && $.defaultView || window;
      if (!q.getSelection)
        return;
      var H = q.getSelection(), G = Z.textContent.length, E = Math.min(X.start, G), U = X.end === void 0 ? E : Math.min(X.end, G);
      if (!H.extend && E > U) {
        var P = U;
        U = E, E = P;
      }
      var O = bP(Z, E), k = bP(Z, U);
      if (O && k) {
        if (H.rangeCount === 1 && H.anchorNode === O.node && H.anchorOffset === O.offset && H.focusNode === k.node && H.focusOffset === k.offset)
          return;
        var C = $.createRange();
        if (C.setStart(O.node, O.offset), H.removeAllRanges(), E > U)
          H.addRange(C), H.extend(k.node, k.offset);
        else
          C.setEnd(k.node, k.offset), H.addRange(C);
      }
    }
    function uP(Z) {
      return Z && Z.nodeType === iX;
    }
    function cP(Z, X) {
      if (!Z || !X)
        return !1;
      else if (Z === X)
        return !0;
      else if (uP(Z))
        return !1;
      else if (uP(X))
        return cP(Z, X.parentNode);
      else if ("contains" in Z)
        return Z.contains(X);
      else if (Z.compareDocumentPosition)
        return !!(Z.compareDocumentPosition(X) & 16);
      else
        return !1;
    }
    function BV(Z) {
      return Z && Z.ownerDocument && cP(Z.ownerDocument.documentElement, Z);
    }
    function CV(Z) {
      try {
        return typeof Z.contentWindow.location.href === "string";
      } catch (X) {
        return !1;
      }
    }
    function pP() {
      var Z = window, X = y4();
      while (X instanceof Z.HTMLIFrameElement) {
        if (CV(X))
          Z = X.contentWindow;
        else
          return X;
        X = y4(Z.document);
      }
      return X;
    }
    function kG(Z) {
      var X = Z && Z.nodeName && Z.nodeName.toLowerCase();
      return X && (X === "input" && (Z.type === "text" || Z.type === "search" || Z.type === "tel" || Z.type === "url" || Z.type === "password") || X === "textarea" || Z.contentEditable === "true");
    }
    function VV() {
      var Z = pP();
      return {
        focusedElem: Z,
        selectionRange: kG(Z) ? IV(Z) : null
      };
    }
    function SV(Z) {
      var X = pP(), $ = Z.focusedElem, q = Z.selectionRange;
      if (X !== $ && BV($)) {
        if (q !== null && kG($))
          _V($, q);
        var H = [], G = $;
        while (G = G.parentNode)
          if (G.nodeType === SQ)
            H.push({
              element: G,
              left: G.scrollLeft,
              top: G.scrollTop
            });
        if (typeof $.focus === "function")
          $.focus();
        for (var E = 0;E < H.length; E++) {
          var U = H[E];
          U.element.scrollLeft = U.left, U.element.scrollTop = U.top;
        }
      }
    }
    function IV(Z) {
      var X;
      if ("selectionStart" in Z)
        X = {
          start: Z.selectionStart,
          end: Z.selectionEnd
        };
      else
        X = kV(Z);
      return X || {
        start: 0,
        end: 0
      };
    }
    function _V(Z, X) {
      var { start: $, end: q } = X;
      if (q === void 0)
        q = $;
      if ("selectionStart" in Z)
        Z.selectionStart = $, Z.selectionEnd = Math.min(q, Z.value.length);
      else
        jV(Z, X);
    }
    var TV = i1 && "documentMode" in document && document.documentMode <= 11;
    function gV() {
      x1("onSelect", ["focusout", "contextmenu", "dragend", "focusin", "keydown", "keyup", "mousedown", "mouseup", "selectionchange"]);
    }
    var AY = null, RG = null, LW = null, jG = !1;
    function xV(Z) {
      if ("selectionStart" in Z && kG(Z))
        return {
          start: Z.selectionStart,
          end: Z.selectionEnd
        };
      else {
        var X = Z.ownerDocument && Z.ownerDocument.defaultView || window, $ = X.getSelection();
        return {
          anchorNode: $.anchorNode,
          anchorOffset: $.anchorOffset,
          focusNode: $.focusNode,
          focusOffset: $.focusOffset
        };
      }
    }
    function vV(Z) {
      return Z.window === Z ? Z.document : Z.nodeType === tX ? Z : Z.ownerDocument;
    }
    function dP(Z, X, $) {
      var q = vV($);
      if (jG || AY == null || AY !== y4(q))
        return;
      var H = xV(AY);
      if (!LW || !AW(LW, H)) {
        LW = H;
        var G = eK(RG, "onSelect");
        if (G.length > 0) {
          var E = new AG("onSelect", "select", null, X, $);
          Z.push({
            event: E,
            listeners: G
          }), E.target = AY;
        }
      }
    }
    function hV(Z, X, $, q, H, G, E) {
      var U = $ ? DY($) : window;
      switch (X) {
        case "focusin":
          if (xP(U) || U.contentEditable === "true")
            AY = U, RG = $, LW = null;
          break;
        case "focusout":
          AY = null, RG = null, LW = null;
          break;
        case "mousedown":
          jG = !0;
          break;
        case "contextmenu":
        case "mouseup":
        case "dragend":
          jG = !1, dP(Z, q, H);
          break;
        case "selectionchange":
          if (TV)
            break;
        case "keydown":
        case "keyup":
          dP(Z, q, H);
      }
    }
    function rK(Z, X) {
      var $ = {};
      return $[Z.toLowerCase()] = X.toLowerCase(), $["Webkit" + Z] = "webkit" + X, $["Moz" + Z] = "moz" + X, $;
    }
    var LY = {
      animationend: rK("Animation", "AnimationEnd"),
      animationiteration: rK("Animation", "AnimationIteration"),
      animationstart: rK("Animation", "AnimationStart"),
      transitionend: rK("Transition", "TransitionEnd")
    }, BG = {}, lP = {};
    if (i1) {
      if (lP = document.createElement("div").style, !("AnimationEvent" in window))
        delete LY.animationend.animation, delete LY.animationiteration.animation, delete LY.animationstart.animation;
      if (!("TransitionEvent" in window))
        delete LY.transitionend.transition;
    }
    function iK(Z) {
      if (BG[Z])
        return BG[Z];
      else if (!LY[Z])
        return Z;
      var X = LY[Z];
      for (var $ in X)
        if (X.hasOwnProperty($) && $ in lP)
          return BG[Z] = X[$];
      return Z;
    }
    var nP = iK("animationend"), sP = iK("animationiteration"), oP = iK("animationstart"), aP = iK("transitionend"), rP = /* @__PURE__ */ new Map, iP = ["abort", "auxClick", "cancel", "canPlay", "canPlayThrough", "click", "close", "contextMenu", "copy", "cut", "drag", "dragEnd", "dragEnter", "dragExit", "dragLeave", "dragOver", "dragStart", "drop", "durationChange", "emptied", "encrypted", "ended", "error", "gotPointerCapture", "input", "invalid", "keyDown", "keyPress", "keyUp", "load", "loadedData", "loadedMetadata", "loadStart", "lostPointerCapture", "mouseDown", "mouseMove", "mouseOut", "mouseOver", "mouseUp", "paste", "pause", "play", "playing", "pointerCancel", "pointerDown", "pointerMove", "pointerOut", "pointerOver", "pointerUp", "progress", "rateChange", "reset", "resize", "seeked", "seeking", "stalled", "submit", "suspend", "timeUpdate", "touchCancel", "touchEnd", "touchStart", "volumeChange", "scroll", "toggle", "touchMove", "waiting", "wheel"];
    function p4(Z, X) {
      rP.set(Z, X), x1(X, [Z]);
    }
    function yV() {
      for (var Z = 0;Z < iP.length; Z++) {
        var X = iP[Z], $ = X.toLowerCase(), q = X[0].toUpperCase() + X.slice(1);
        p4($, "on" + q);
      }
      p4(nP, "onAnimationEnd"), p4(sP, "onAnimationIteration"), p4(oP, "onAnimationStart"), p4("dblclick", "onDoubleClick"), p4("focusin", "onFocus"), p4("focusout", "onBlur"), p4(aP, "onTransitionEnd");
    }
    function fV(Z, X, $, q, H, G, E) {
      var U = rP.get(X);
      if (U === void 0)
        return;
      var P = AG, O = X;
      switch (X) {
        case "keypress":
          if (nK(q) === 0)
            return;
        case "keydown":
        case "keyup":
          P = mC;
          break;
        case "focusin":
          O = "focus", P = wG;
          break;
        case "focusout":
          O = "blur", P = wG;
          break;
        case "beforeblur":
        case "afterblur":
          P = wG;
          break;
        case "click":
          if (q.button === 2)
            return;
        case "auxclick":
        case "dblclick":
        case "mousedown":
        case "mousemove":
        case "mouseup":
        case "mouseout":
        case "mouseover":
        case "contextmenu":
          P = kP;
          break;
        case "drag":
        case "dragend":
        case "dragenter":
        case "dragexit":
        case "dragleave":
        case "dragover":
        case "dragstart":
        case "drop":
          P = jC;
          break;
        case "touchcancel":
        case "touchend":
        case "touchmove":
        case "touchstart":
          P = cC;
          break;
        case nP:
        case sP:
        case oP:
          P = VC;
          break;
        case aP:
          P = dC;
          break;
        case "scroll":
          P = DC;
          break;
        case "wheel":
          P = nC;
          break;
        case "copy":
        case "cut":
        case "paste":
          P = IC;
          break;
        case "gotpointercapture":
        case "lostpointercapture":
        case "pointercancel":
        case "pointerdown":
        case "pointermove":
        case "pointerout":
        case "pointerover":
        case "pointerup":
          P = jP;
          break;
      }
      var k = (G & pq) !== 0;
      {
        var C = !k && X === "scroll", B = cV($, U, q.type, k, C);
        if (B.length > 0) {
          var v = new P(U, O, null, q, H);
          Z.push({
            event: v,
            listeners: B
          });
        }
      }
    }
    yV(), OV(), qV(), gV(), aC();
    function mV(Z, X, $, q, H, G, E) {
      fV(Z, X, $, q, H, G);
      var U = (G & xj) === 0;
      if (U)
        wV(Z, X, $, q, H), LV(Z, X, $, q, H), hV(Z, X, $, q, H), JV(Z, X, $, q, H);
    }
    var OW = ["abort", "canplay", "canplaythrough", "durationchange", "emptied", "encrypted", "ended", "error", "loadeddata", "loadedmetadata", "loadstart", "pause", "play", "playing", "progress", "ratechange", "resize", "seeked", "seeking", "stalled", "suspend", "timeupdate", "volumechange", "waiting"], CG = new Set(["cancel", "close", "invalid", "load", "scroll", "toggle"].concat(OW));
    function tP(Z, X, $) {
      var q = Z.type || "unknown-event";
      Z.currentTarget = $, nj(q, X, void 0, Z), Z.currentTarget = null;
    }
    function bV(Z, X, $) {
      var q;
      if ($)
        for (var H = X.length - 1;H >= 0; H--) {
          var G = X[H], E = G.instance, U = G.currentTarget, P = G.listener;
          if (E !== q && Z.isPropagationStopped())
            return;
          tP(Z, P, U), q = E;
        }
      else
        for (var O = 0;O < X.length; O++) {
          var k = X[O], C = k.instance, B = k.currentTarget, v = k.listener;
          if (C !== q && Z.isPropagationStopped())
            return;
          tP(Z, v, B), q = C;
        }
    }
    function eP(Z, X) {
      var $ = (X & pq) !== 0;
      for (var q = 0;q < Z.length; q++) {
        var H = Z[q], G = H.event, E = H.listeners;
        bV(G, E, $);
      }
      sj();
    }
    function uV(Z, X, $, q, H) {
      var G = D7($), E = [];
      mV(E, Z, q, $, G, X), eP(E, X);
    }
    function W6(Z, X) {
      if (!CG.has(Z))
        K('Did not expect a listenToNonDelegatedEvent() call for "%s". This is a bug in React. Please file an issue.', Z);
      var $ = !1, q = AI(X), H = lV(Z, $);
      if (!q.has(H))
        QA(X, Z, M7, $), q.add(H);
    }
    function VG(Z, X, $) {
      if (CG.has(Z) && !X)
        K('Did not expect a listenToNativeEvent() call for "%s" in the bubble phase. This is a bug in React. Please file an issue.', Z);
      var q = 0;
      if (X)
        q |= pq;
      QA($, Z, q, X);
    }
    var tK = "_reactListening" + Math.random().toString(36).slice(2);
    function wW(Z) {
      if (!Z[tK]) {
        Z[tK] = !0, o1.forEach(function($) {
          if ($ !== "selectionchange") {
            if (!CG.has($))
              VG($, !1, Z);
            VG($, !0, Z);
          }
        });
        var X = Z.nodeType === tX ? Z : Z.ownerDocument;
        if (X !== null) {
          if (!X[tK])
            X[tK] = !0, VG("selectionchange", !1, X);
        }
      }
    }
    function QA(Z, X, $, q, H) {
      var G = NC(Z, X, $), E = void 0;
      if (j7) {
        if (X === "touchstart" || X === "touchmove" || X === "wheel")
          E = !0;
      }
      Z = Z;
      var U;
      if (q)
        if (E !== void 0)
          U = LC(Z, X, G, E);
        else
          U = AC(Z, X, G);
      else if (E !== void 0)
        U = OC(Z, X, G, E);
      else
        U = PC(Z, X, G);
    }
    function ZA(Z, X) {
      return Z === X || Z.nodeType === f6 && Z.parentNode === X;
    }
    function SG(Z, X, $, q, H) {
      var G = q;
      if ((X & IU) === 0 && (X & M7) === 0) {
        var E = H;
        if (q !== null) {
          var U = q;
          Q:
            while (!0) {
              if (U === null)
                return;
              var P = U.tag;
              if (P === w || P === D) {
                var O = U.stateNode.containerInfo;
                if (ZA(O, E))
                  break;
                if (P === D) {
                  var k = U.return;
                  while (k !== null) {
                    var C = k.tag;
                    if (C === w || C === D) {
                      var B = k.stateNode.containerInfo;
                      if (ZA(B, E))
                        return;
                    }
                    k = k.return;
                  }
                }
                while (O !== null) {
                  var v = q$(O);
                  if (v === null)
                    return;
                  var h = v.tag;
                  if (h === R || h === V) {
                    U = G = v;
                    continue Q;
                  }
                  O = O.parentNode;
                }
              }
              U = U.return;
            }
        }
      }
      hU(function() {
        return uV(Z, X, $, G);
      });
    }
    function MW(Z, X, $) {
      return {
        instance: Z,
        listener: X,
        currentTarget: $
      };
    }
    function cV(Z, X, $, q, H, G) {
      var E = X !== null ? X + "Capture" : null, U = q ? E : X, P = [], O = Z, k = null;
      while (O !== null) {
        var C = O, B = C.stateNode, v = C.tag;
        if (v === R && B !== null) {
          if (k = B, U !== null) {
            var h = lq(O, U);
            if (h != null)
              P.push(MW(O, h, k));
          }
        }
        if (H)
          break;
        O = O.return;
      }
      return P;
    }
    function eK(Z, X) {
      var $ = X + "Capture", q = [], H = Z;
      while (H !== null) {
        var G = H, E = G.stateNode, U = G.tag;
        if (U === R && E !== null) {
          var P = E, O = lq(H, $);
          if (O != null)
            q.unshift(MW(H, O, P));
          var k = lq(H, X);
          if (k != null)
            q.push(MW(H, k, P));
        }
        H = H.return;
      }
      return q;
    }
    function OY(Z) {
      if (Z === null)
        return null;
      do
        Z = Z.return;
      while (Z && Z.tag !== R);
      if (Z)
        return Z;
      return null;
    }
    function pV(Z, X) {
      var $ = Z, q = X, H = 0;
      for (var G = $;G; G = OY(G))
        H++;
      var E = 0;
      for (var U = q;U; U = OY(U))
        E++;
      while (H - E > 0)
        $ = OY($), H--;
      while (E - H > 0)
        q = OY(q), E--;
      var P = H;
      while (P--) {
        if ($ === q || q !== null && $ === q.alternate)
          return $;
        $ = OY($), q = OY(q);
      }
      return null;
    }
    function XA(Z, X, $, q, H) {
      var G = X._reactName, E = [], U = $;
      while (U !== null) {
        if (U === q)
          break;
        var P = U, O = P.alternate, k = P.stateNode, C = P.tag;
        if (O !== null && O === q)
          break;
        if (C === R && k !== null) {
          var B = k;
          if (H) {
            var v = lq(U, G);
            if (v != null)
              E.unshift(MW(U, v, B));
          } else if (!H) {
            var h = lq(U, G);
            if (h != null)
              E.push(MW(U, h, B));
          }
        }
        U = U.return;
      }
      if (E.length !== 0)
        Z.push({
          event: X,
          listeners: E
        });
    }
    function dV(Z, X, $, q, H) {
      var G = q && H ? pV(q, H) : null;
      if (q !== null)
        XA(Z, X, q, G, !1);
      if (H !== null && $ !== null)
        XA(Z, $, H, G, !0);
    }
    function lV(Z, X) {
      return Z + "__" + (X ? "capture" : "bubble");
    }
    var IQ = !1, DW = "dangerouslySetInnerHTML", Q9 = "suppressContentEditableWarning", d4 = "suppressHydrationWarning", JA = "autoFocus", $$ = "children", Y$ = "style", Z9 = "__html", IG, X9, kW, $A, J9, YA, qA;
    IG = {
      dialog: !0,
      webview: !0
    }, X9 = function(Z, X) {
      Cj(Z, X), Vj(Z, X), gj(Z, X, {
        registrationNameDependencies: f1,
        possibleRegistrationNames: E6
      });
    }, YA = i1 && !document.documentMode, kW = function(Z, X, $) {
      if (IQ)
        return;
      var q = $9($), H = $9(X);
      if (H === q)
        return;
      IQ = !0, K("Prop `%s` did not match. Server: %s Client: %s", Z, JSON.stringify(H), JSON.stringify(q));
    }, $A = function(Z) {
      if (IQ)
        return;
      IQ = !0;
      var X = [];
      Z.forEach(function($) {
        X.push($);
      }), K("Extra attributes from the server: %s", X);
    }, J9 = function(Z, X) {
      if (X === !1)
        K("Expected `%s` listener to be a function, instead got `false`.\n\nIf you used to conditionally omit it with %s={condition && value}, pass %s={condition ? value : undefined} instead.", Z, Z, Z);
      else
        K("Expected `%s` listener to be a function, instead got a value of `%s` type.", Z, typeof X);
    }, qA = function(Z, X) {
      var $ = Z.namespaceURI === rX ? Z.ownerDocument.createElement(Z.tagName) : Z.ownerDocument.createElementNS(Z.namespaceURI, Z.tagName);
      return $.innerHTML = X, $.innerHTML;
    };
    var nV = /\r\n?/g, sV = /\u0000|\uFFFD/g;
    function $9(Z) {
      q8(Z);
      var X = typeof Z === "string" ? Z : "" + Z;
      return X.replace(nV, `
`).replace(sV, "");
    }
    function Y9(Z, X, $, q) {
      var H = $9(X), G = $9(Z);
      if (G === H)
        return;
      if (q) {
        if (!IQ)
          IQ = !0, K('Text content did not match. Server: "%s" Client: "%s"', G, H);
      }
      if ($ && N0)
        throw new Error("Text content does not match server-rendered HTML.");
    }
    function WA(Z) {
      return Z.nodeType === tX ? Z : Z.ownerDocument;
    }
    function oV() {}
    function q9(Z) {
      Z.onclick = oV;
    }
    function aV(Z, X, $, q, H) {
      for (var G in q) {
        if (!q.hasOwnProperty(G))
          continue;
        var E = q[G];
        if (G === Y$) {
          if (E)
            Object.freeze(E);
          RU(X, E);
        } else if (G === DW) {
          var U = E ? E[Z9] : void 0;
          if (U != null)
            OU(X, U);
        } else if (G === $$) {
          if (typeof E === "string") {
            var P = Z !== "textarea" || E !== "";
            if (P)
              CK(X, E);
          } else if (typeof E === "number")
            CK(X, "" + E);
        } else if (G === Q9 || G === d4)
          ;
        else if (G === JA)
          ;
        else if (f1.hasOwnProperty(G)) {
          if (E != null) {
            if (typeof E !== "function")
              J9(G, E);
            if (G === "onScroll")
              W6("scroll", X);
          }
        } else if (E != null)
          BQ(X, G, E, H);
      }
    }
    function rV(Z, X, $, q) {
      for (var H = 0;H < X.length; H += 2) {
        var G = X[H], E = X[H + 1];
        if (G === Y$)
          RU(Z, E);
        else if (G === DW)
          OU(Z, E);
        else if (G === $$)
          CK(Z, E);
        else
          BQ(Z, G, E, q);
      }
    }
    function iV(Z, X, $, q) {
      var H, G = WA($), E, U = q;
      if (U === rX)
        U = U7(Z);
      if (U === rX) {
        if (H = nJ(Z, X), !H && Z !== Z.toLowerCase())
          K("<%s /> is using incorrect casing. Use PascalCase for React components, or lowercase for HTML elements.", Z);
        if (Z === "script") {
          var P = G.createElement("div");
          P.innerHTML = "<script></script>";
          var O = P.firstChild;
          E = P.removeChild(O);
        } else if (typeof X.is === "string")
          E = G.createElement(Z, {
            is: X.is
          });
        else if (E = G.createElement(Z), Z === "select") {
          var k = E;
          if (X.multiple)
            k.multiple = !0;
          else if (X.size)
            k.size = X.size;
        }
      } else
        E = G.createElementNS(U, Z);
      if (U === rX) {
        if (!H && Object.prototype.toString.call(E) === "[object HTMLUnknownElement]" && !Z0.call(IG, Z))
          IG[Z] = !0, K("The tag <%s> is unrecognized in this browser. If you meant to render a React component, start its name with an uppercase letter.", Z);
      }
      return E;
    }
    function tV(Z, X) {
      return WA(X).createTextNode(Z);
    }
    function eV(Z, X, $, q) {
      var H = nJ(X, $);
      X9(X, $);
      var G;
      switch (X) {
        case "dialog":
          W6("cancel", Z), W6("close", Z), G = $;
          break;
        case "iframe":
        case "object":
        case "embed":
          W6("load", Z), G = $;
          break;
        case "video":
        case "audio":
          for (var E = 0;E < OW.length; E++)
            W6(OW[E], Z);
          G = $;
          break;
        case "source":
          W6("error", Z), G = $;
          break;
        case "img":
        case "image":
        case "link":
          W6("error", Z), W6("load", Z), G = $;
          break;
        case "details":
          W6("toggle", Z), G = $;
          break;
        case "input":
          j(Z, $), G = A(Z, $), W6("invalid", Z);
          break;
        case "option":
          Q6(Z, $), G = $;
          break;
        case "select":
          uq(Z, $), G = bq(Z, $), W6("invalid", Z);
          break;
        case "textarea":
          PU(Z, $), G = E7(Z, $), W6("invalid", Z);
          break;
        default:
          G = $;
      }
      switch (w7(X, G), aV(X, Z, q, G, H), X) {
        case "input":
          oX(Z), e(Z, $, !1);
          break;
        case "textarea":
          oX(Z), LU(Z);
          break;
        case "option":
          q6(Z, $);
          break;
        case "select":
          N7(Z, $);
          break;
        default:
          if (typeof G.onClick === "function")
            q9(Z);
          break;
      }
    }
    function QS(Z, X, $, q, H) {
      X9(X, q);
      var G = null, E, U;
      switch (X) {
        case "input":
          E = A(Z, $), U = A(Z, q), G = [];
          break;
        case "select":
          E = bq(Z, $), U = bq(Z, q), G = [];
          break;
        case "textarea":
          E = E7(Z, $), U = E7(Z, q), G = [];
          break;
        default:
          if (E = $, U = q, typeof E.onClick !== "function" && typeof U.onClick === "function")
            q9(Z);
          break;
      }
      w7(X, U);
      var P, O, k = null;
      for (P in E) {
        if (U.hasOwnProperty(P) || !E.hasOwnProperty(P) || E[P] == null)
          continue;
        if (P === Y$) {
          var C = E[P];
          for (O in C)
            if (C.hasOwnProperty(O)) {
              if (!k)
                k = {};
              k[O] = "";
            }
        } else if (P === DW || P === $$)
          ;
        else if (P === Q9 || P === d4)
          ;
        else if (P === JA)
          ;
        else if (f1.hasOwnProperty(P)) {
          if (!G)
            G = [];
        } else
          (G = G || []).push(P, null);
      }
      for (P in U) {
        var B = U[P], v = E != null ? E[P] : void 0;
        if (!U.hasOwnProperty(P) || B === v || B == null && v == null)
          continue;
        if (P === Y$) {
          if (B)
            Object.freeze(B);
          if (v) {
            for (O in v)
              if (v.hasOwnProperty(O) && (!B || !B.hasOwnProperty(O))) {
                if (!k)
                  k = {};
                k[O] = "";
              }
            for (O in B)
              if (B.hasOwnProperty(O) && v[O] !== B[O]) {
                if (!k)
                  k = {};
                k[O] = B[O];
              }
          } else {
            if (!k) {
              if (!G)
                G = [];
              G.push(P, k);
            }
            k = B;
          }
        } else if (P === DW) {
          var h = B ? B[Z9] : void 0, f = v ? v[Z9] : void 0;
          if (h != null) {
            if (f !== h)
              (G = G || []).push(P, h);
          }
        } else if (P === $$) {
          if (typeof B === "string" || typeof B === "number")
            (G = G || []).push(P, "" + B);
        } else if (P === Q9 || P === d4)
          ;
        else if (f1.hasOwnProperty(P)) {
          if (B != null) {
            if (typeof B !== "function")
              J9(P, B);
            if (P === "onScroll")
              W6("scroll", Z);
          }
          if (!G && v !== B)
            G = [];
        } else
          (G = G || []).push(P, B);
      }
      if (k)
        Oj(k, U[Y$]), (G = G || []).push(Y$, k);
      return G;
    }
    function ZS(Z, X, $, q, H) {
      if ($ === "input" && H.type === "radio" && H.name != null)
        x(Z, H);
      var G = nJ($, q), E = nJ($, H);
      switch (rV(Z, X, G, E), $) {
        case "input":
          m(Z, H);
          break;
        case "textarea":
          AU(Z, H);
          break;
        case "select":
          rR(Z, H);
          break;
      }
    }
    function XS(Z) {
      {
        var X = Z.toLowerCase();
        if (!VK.hasOwnProperty(X))
          return null;
        return VK[X] || null;
      }
    }
    function JS(Z, X, $, q, H, G, E) {
      var U, P;
      switch (U = nJ(X, $), X9(X, $), X) {
        case "dialog":
          W6("cancel", Z), W6("close", Z);
          break;
        case "iframe":
        case "object":
        case "embed":
          W6("load", Z);
          break;
        case "video":
        case "audio":
          for (var O = 0;O < OW.length; O++)
            W6(OW[O], Z);
          break;
        case "source":
          W6("error", Z);
          break;
        case "img":
        case "image":
        case "link":
          W6("error", Z), W6("load", Z);
          break;
        case "details":
          W6("toggle", Z);
          break;
        case "input":
          j(Z, $), W6("invalid", Z);
          break;
        case "option":
          Q6(Z, $);
          break;
        case "select":
          uq(Z, $), W6("invalid", Z);
          break;
        case "textarea":
          PU(Z, $), W6("invalid", Z);
          break;
      }
      w7(X, $);
      {
        P = /* @__PURE__ */ new Set;
        var k = Z.attributes;
        for (var C = 0;C < k.length; C++) {
          var B = k[C].name.toLowerCase();
          switch (B) {
            case "value":
              break;
            case "checked":
              break;
            case "selected":
              break;
            default:
              P.add(k[C].name);
          }
        }
      }
      var v = null;
      for (var h in $) {
        if (!$.hasOwnProperty(h))
          continue;
        var f = $[h];
        if (h === $$) {
          if (typeof f === "string") {
            if (Z.textContent !== f) {
              if ($[d4] !== !0)
                Y9(Z.textContent, f, G, E);
              v = [$$, f];
            }
          } else if (typeof f === "number") {
            if (Z.textContent !== "" + f) {
              if ($[d4] !== !0)
                Y9(Z.textContent, f, G, E);
              v = [$$, "" + f];
            }
          }
        } else if (f1.hasOwnProperty(h)) {
          if (f != null) {
            if (typeof f !== "function")
              J9(h, f);
            if (h === "onScroll")
              W6("scroll", Z);
          }
        } else if (E && !0 && typeof U === "boolean") {
          var q0 = void 0, k0 = U && _1 ? null : l8(h);
          if ($[d4] === !0)
            ;
          else if (h === Q9 || h === d4 || h === "value" || h === "checked" || h === "selected")
            ;
          else if (h === DW) {
            var w0 = Z.innerHTML, N1 = f ? f[Z9] : void 0;
            if (N1 != null) {
              var E1 = qA(Z, N1);
              if (E1 !== w0)
                kW(h, w0, E1);
            }
          } else if (h === Y$) {
            if (P.delete(h), YA) {
              var _ = Aj(f);
              if (q0 = Z.getAttribute("style"), _ !== q0)
                kW(h, q0, _);
            }
          } else if (U && !_1) {
            if (P.delete(h.toLowerCase()), q0 = y6(Z, h, f), f !== q0)
              kW(h, q0, f);
          } else if (!h1(h, k0, U) && !a1(h, f, k0, U)) {
            var b = !1;
            if (k0 !== null)
              P.delete(k0.attributeName), q0 = G8(Z, h, f, k0);
            else {
              var T = q;
              if (T === rX)
                T = U7(X);
              if (T === rX)
                P.delete(h.toLowerCase());
              else {
                var a = XS(h);
                if (a !== null && a !== h)
                  b = !0, P.delete(a);
                P.delete(h);
              }
              q0 = y6(Z, h, f);
            }
            var E0 = _1;
            if (!E0 && f !== q0 && !b)
              kW(h, q0, f);
          }
        }
      }
      if (E) {
        if (P.size > 0 && $[d4] !== !0)
          $A(P);
      }
      switch (X) {
        case "input":
          oX(Z), e(Z, $, !0);
          break;
        case "textarea":
          oX(Z), LU(Z);
          break;
        case "select":
        case "option":
          break;
        default:
          if (typeof $.onClick === "function")
            q9(Z);
          break;
      }
      return v;
    }
    function $S(Z, X, $) {
      var q = Z.nodeValue !== X;
      return q;
    }
    function _G(Z, X) {
      {
        if (IQ)
          return;
        IQ = !0, K("Did not expect server HTML to contain a <%s> in <%s>.", X.nodeName.toLowerCase(), Z.nodeName.toLowerCase());
      }
    }
    function TG(Z, X) {
      {
        if (IQ)
          return;
        IQ = !0, K('Did not expect server HTML to contain the text node "%s" in <%s>.', X.nodeValue, Z.nodeName.toLowerCase());
      }
    }
    function gG(Z, X, $) {
      {
        if (IQ)
          return;
        IQ = !0, K("Expected server HTML to contain a matching <%s> in <%s>.", X, Z.nodeName.toLowerCase());
      }
    }
    function xG(Z, X) {
      {
        if (X === "")
          return;
        if (IQ)
          return;
        IQ = !0, K('Expected server HTML to contain a matching text node for "%s" in <%s>.', X, Z.nodeName.toLowerCase());
      }
    }
    function YS(Z, X, $) {
      switch (X) {
        case "input":
          T0(Z, $);
          return;
        case "textarea":
          tR(Z, $);
          return;
        case "select":
          iR(Z, $);
          return;
      }
    }
    var RW = function() {}, jW = function() {};
    {
      var qS = ["address", "applet", "area", "article", "aside", "base", "basefont", "bgsound", "blockquote", "body", "br", "button", "caption", "center", "col", "colgroup", "dd", "details", "dir", "div", "dl", "dt", "embed", "fieldset", "figcaption", "figure", "footer", "form", "frame", "frameset", "h1", "h2", "h3", "h4", "h5", "h6", "head", "header", "hgroup", "hr", "html", "iframe", "img", "input", "isindex", "li", "link", "listing", "main", "marquee", "menu", "menuitem", "meta", "nav", "noembed", "noframes", "noscript", "object", "ol", "p", "param", "plaintext", "pre", "script", "section", "select", "source", "style", "summary", "table", "tbody", "td", "template", "textarea", "tfoot", "th", "thead", "title", "tr", "track", "ul", "wbr", "xmp"], KA = [
        "applet",
        "caption",
        "html",
        "table",
        "td",
        "th",
        "marquee",
        "object",
        "template",
        "foreignObject",
        "desc",
        "title"
      ], WS = KA.concat(["button"]), KS = ["dd", "dt", "li", "option", "optgroup", "p", "rp", "rt"], HA = {
        current: null,
        formTag: null,
        aTagInScope: null,
        buttonTagInScope: null,
        nobrTagInScope: null,
        pTagInButtonScope: null,
        listItemTagAutoclosing: null,
        dlItemTagAutoclosing: null
      };
      jW = function(Z, X) {
        var $ = K1({}, Z || HA), q = {
          tag: X
        };
        if (KA.indexOf(X) !== -1)
          $.aTagInScope = null, $.buttonTagInScope = null, $.nobrTagInScope = null;
        if (WS.indexOf(X) !== -1)
          $.pTagInButtonScope = null;
        if (qS.indexOf(X) !== -1 && X !== "address" && X !== "div" && X !== "p")
          $.listItemTagAutoclosing = null, $.dlItemTagAutoclosing = null;
        if ($.current = q, X === "form")
          $.formTag = q;
        if (X === "a")
          $.aTagInScope = q;
        if (X === "button")
          $.buttonTagInScope = q;
        if (X === "nobr")
          $.nobrTagInScope = q;
        if (X === "p")
          $.pTagInButtonScope = q;
        if (X === "li")
          $.listItemTagAutoclosing = q;
        if (X === "dd" || X === "dt")
          $.dlItemTagAutoclosing = q;
        return $;
      };
      var HS = function(Z, X) {
        switch (X) {
          case "select":
            return Z === "option" || Z === "optgroup" || Z === "#text";
          case "optgroup":
            return Z === "option" || Z === "#text";
          case "option":
            return Z === "#text";
          case "tr":
            return Z === "th" || Z === "td" || Z === "style" || Z === "script" || Z === "template";
          case "tbody":
          case "thead":
          case "tfoot":
            return Z === "tr" || Z === "style" || Z === "script" || Z === "template";
          case "colgroup":
            return Z === "col" || Z === "template";
          case "table":
            return Z === "caption" || Z === "colgroup" || Z === "tbody" || Z === "tfoot" || Z === "thead" || Z === "style" || Z === "script" || Z === "template";
          case "head":
            return Z === "base" || Z === "basefont" || Z === "bgsound" || Z === "link" || Z === "meta" || Z === "title" || Z === "noscript" || Z === "noframes" || Z === "style" || Z === "script" || Z === "template";
          case "html":
            return Z === "head" || Z === "body" || Z === "frameset";
          case "frameset":
            return Z === "frame";
          case "#document":
            return Z === "html";
        }
        switch (Z) {
          case "h1":
          case "h2":
          case "h3":
          case "h4":
          case "h5":
          case "h6":
            return X !== "h1" && X !== "h2" && X !== "h3" && X !== "h4" && X !== "h5" && X !== "h6";
          case "rp":
          case "rt":
            return KS.indexOf(X) === -1;
          case "body":
          case "caption":
          case "col":
          case "colgroup":
          case "frameset":
          case "frame":
          case "head":
          case "html":
          case "tbody":
          case "td":
          case "tfoot":
          case "th":
          case "thead":
          case "tr":
            return X == null;
        }
        return !0;
      }, GS = function(Z, X) {
        switch (Z) {
          case "address":
          case "article":
          case "aside":
          case "blockquote":
          case "center":
          case "details":
          case "dialog":
          case "dir":
          case "div":
          case "dl":
          case "fieldset":
          case "figcaption":
          case "figure":
          case "footer":
          case "header":
          case "hgroup":
          case "main":
          case "menu":
          case "nav":
          case "ol":
          case "p":
          case "section":
          case "summary":
          case "ul":
          case "pre":
          case "listing":
          case "table":
          case "hr":
          case "xmp":
          case "h1":
          case "h2":
          case "h3":
          case "h4":
          case "h5":
          case "h6":
            return X.pTagInButtonScope;
          case "form":
            return X.formTag || X.pTagInButtonScope;
          case "li":
            return X.listItemTagAutoclosing;
          case "dd":
          case "dt":
            return X.dlItemTagAutoclosing;
          case "button":
            return X.buttonTagInScope;
          case "a":
            return X.aTagInScope;
          case "nobr":
            return X.nobrTagInScope;
        }
        return null;
      }, GA = {};
      RW = function(Z, X, $) {
        $ = $ || HA;
        var q = $.current, H = q && q.tag;
        if (X != null) {
          if (Z != null)
            K("validateDOMNesting: when childText is passed, childTag should be null");
          Z = "#text";
        }
        var G = HS(Z, H) ? null : q, E = G ? null : GS(Z, $), U = G || E;
        if (!U)
          return;
        var P = U.tag, O = !!G + "|" + Z + "|" + P;
        if (GA[O])
          return;
        GA[O] = !0;
        var k = Z, C = "";
        if (Z === "#text")
          if (/\S/.test(X))
            k = "Text nodes";
          else
            k = "Whitespace text nodes", C = " Make sure you don't have any extra whitespace between tags on each line of your source code.";
        else
          k = "<" + Z + ">";
        if (G) {
          var B = "";
          if (P === "table" && Z === "tr")
            B += " Add a <tbody>, <thead> or <tfoot> to your code to match the DOM tree generated by the browser.";
          K("validateDOMNesting(...): %s cannot appear as a child of <%s>.%s%s", k, P, C, B);
        } else
          K("validateDOMNesting(...): %s cannot appear as a descendant of <%s>.", k, P);
      };
    }
    var W9 = "suppressHydrationWarning", K9 = "$", H9 = "/$", BW = "$?", CW = "$!", zS = "style", vG = null, hG = null;
    function NS(Z) {
      var X, $, q = Z.nodeType;
      switch (q) {
        case tX:
        case A7: {
          X = q === tX ? "#document" : "#fragment";
          var H = Z.documentElement;
          $ = H ? H.namespaceURI : P7(null, "");
          break;
        }
        default: {
          var G = q === f6 ? Z.parentNode : Z, E = G.namespaceURI || null;
          X = G.tagName, $ = P7(E, X);
          break;
        }
      }
      {
        var U = X.toLowerCase(), P = jW(null, U);
        return {
          namespace: $,
          ancestorInfo: P
        };
      }
    }
    function ES(Z, X, $) {
      {
        var q = Z, H = P7(q.namespace, X), G = jW(q.ancestorInfo, X);
        return {
          namespace: H,
          ancestorInfo: G
        };
      }
    }
    function yG(Z) {
      return Z;
    }
    function FS(Z) {
      vG = zC(), hG = VV();
      var X = null;
      return LP(!1), X;
    }
    function US(Z) {
      SV(hG), LP(vG), vG = null, hG = null;
    }
    function PS(Z, X, $, q, H) {
      var G;
      {
        var E = q;
        if (RW(Z, null, E.ancestorInfo), typeof X.children === "string" || typeof X.children === "number") {
          var U = "" + X.children, P = jW(E.ancestorInfo, Z);
          RW(null, U, P);
        }
        G = E.namespace;
      }
      var O = iV(Z, X, $, G);
      return IW(H, O), lG(O, X), O;
    }
    function AS(Z, X) {
      Z.appendChild(X);
    }
    function LS(Z, X, $, q, H) {
      switch (eV(Z, X, $, q), X) {
        case "button":
        case "input":
        case "select":
        case "textarea":
          return !!$.autoFocus;
        case "img":
          return !0;
        default:
          return !1;
      }
    }
    function OS(Z, X, $, q, H, G) {
      {
        var E = G;
        if (typeof q.children !== typeof $.children && (typeof q.children === "string" || typeof q.children === "number")) {
          var U = "" + q.children, P = jW(E.ancestorInfo, X);
          RW(null, U, P);
        }
      }
      return QS(Z, X, $, q);
    }
    function fG(Z, X) {
      return Z === "textarea" || Z === "noscript" || typeof X.children === "string" || typeof X.children === "number" || typeof X.dangerouslySetInnerHTML === "object" && X.dangerouslySetInnerHTML !== null && X.dangerouslySetInnerHTML.__html != null;
    }
    function wS(Z, X, $, q) {
      {
        var H = $;
        RW(null, Z, H.ancestorInfo);
      }
      var G = tV(Z, X);
      return IW(q, G), G;
    }
    function MS() {
      var Z = window.event;
      if (Z === void 0)
        return Y4;
      return OP(Z.type);
    }
    var mG = typeof setTimeout === "function" ? setTimeout : void 0, DS = typeof clearTimeout === "function" ? clearTimeout : void 0, bG = -1, zA = typeof Promise === "function" ? Promise : void 0, kS = typeof queueMicrotask === "function" ? queueMicrotask : typeof zA !== "undefined" ? function(Z) {
      return zA.resolve(null).then(Z).catch(RS);
    } : mG;
    function RS(Z) {
      setTimeout(function() {
        throw Z;
      });
    }
    function jS(Z, X, $, q) {
      switch (X) {
        case "button":
        case "input":
        case "select":
        case "textarea":
          if ($.autoFocus)
            Z.focus();
          return;
        case "img": {
          if ($.src)
            Z.src = $.src;
          return;
        }
      }
    }
    function BS(Z, X, $, q, H, G) {
      ZS(Z, X, $, q, H), lG(Z, H);
    }
    function NA(Z) {
      CK(Z, "");
    }
    function CS(Z, X, $) {
      Z.nodeValue = $;
    }
    function VS(Z, X) {
      Z.appendChild(X);
    }
    function SS(Z, X) {
      var $;
      if (Z.nodeType === f6)
        $ = Z.parentNode, $.insertBefore(X, Z);
      else
        $ = Z, $.appendChild(X);
      var q = Z._reactRootContainer;
      if ((q === null || q === void 0) && $.onclick === null)
        q9($);
    }
    function IS(Z, X, $) {
      Z.insertBefore(X, $);
    }
    function _S(Z, X, $) {
      if (Z.nodeType === f6)
        Z.parentNode.insertBefore(X, $);
      else
        Z.insertBefore(X, $);
    }
    function TS(Z, X) {
      Z.removeChild(X);
    }
    function gS(Z, X) {
      if (Z.nodeType === f6)
        Z.parentNode.removeChild(X);
      else
        Z.removeChild(X);
    }
    function uG(Z, X) {
      var $ = X, q = 0;
      do {
        var H = $.nextSibling;
        if (Z.removeChild($), H && H.nodeType === f6) {
          var G = H.data;
          if (G === H9)
            if (q === 0) {
              Z.removeChild(H), HW(X);
              return;
            } else
              q--;
          else if (G === K9 || G === BW || G === CW)
            q++;
        }
        $ = H;
      } while ($);
      HW(X);
    }
    function xS(Z, X) {
      if (Z.nodeType === f6)
        uG(Z.parentNode, X);
      else if (Z.nodeType === SQ)
        uG(Z, X);
      HW(Z);
    }
    function vS(Z) {
      Z = Z;
      var X = Z.style;
      if (typeof X.setProperty === "function")
        X.setProperty("display", "none", "important");
      else
        X.display = "none";
    }
    function hS(Z) {
      Z.nodeValue = "";
    }
    function yS(Z, X) {
      Z = Z;
      var $ = X[zS], q = $ !== void 0 && $ !== null && $.hasOwnProperty("display") ? $.display : null;
      Z.style.display = L7("display", q);
    }
    function fS(Z, X) {
      Z.nodeValue = X;
    }
    function mS(Z) {
      if (Z.nodeType === SQ)
        Z.textContent = "";
      else if (Z.nodeType === tX) {
        if (Z.documentElement)
          Z.removeChild(Z.documentElement);
      }
    }
    function bS(Z, X, $) {
      if (Z.nodeType !== SQ || X.toLowerCase() !== Z.nodeName.toLowerCase())
        return null;
      return Z;
    }
    function uS(Z, X) {
      if (X === "" || Z.nodeType !== iX)
        return null;
      return Z;
    }
    function cS(Z) {
      if (Z.nodeType !== f6)
        return null;
      return Z;
    }
    function EA(Z) {
      return Z.data === BW;
    }
    function cG(Z) {
      return Z.data === CW;
    }
    function pS(Z) {
      var X = Z.nextSibling && Z.nextSibling.dataset, $, q, H;
      if (X)
        $ = X.dgst, q = X.msg, H = X.stck;
      return {
        message: q,
        digest: $,
        stack: H
      };
    }
    function dS(Z, X) {
      Z._reactRetry = X;
    }
    function G9(Z) {
      for (;Z != null; Z = Z.nextSibling) {
        var X = Z.nodeType;
        if (X === SQ || X === iX)
          break;
        if (X === f6) {
          var $ = Z.data;
          if ($ === K9 || $ === CW || $ === BW)
            break;
          if ($ === H9)
            return null;
        }
      }
      return Z;
    }
    function VW(Z) {
      return G9(Z.nextSibling);
    }
    function lS(Z) {
      return G9(Z.firstChild);
    }
    function nS(Z) {
      return G9(Z.firstChild);
    }
    function sS(Z) {
      return G9(Z.nextSibling);
    }
    function oS(Z, X, $, q, H, G, E) {
      IW(G, Z), lG(Z, $);
      var U;
      {
        var P = H;
        U = P.namespace;
      }
      var O = (G.mode & A1) !== B0;
      return JS(Z, X, $, U, q, O, E);
    }
    function aS(Z, X, $, q) {
      IW($, Z);
      var H = ($.mode & A1) !== B0;
      return $S(Z, X);
    }
    function rS(Z, X) {
      IW(X, Z);
    }
    function iS(Z) {
      var X = Z.nextSibling, $ = 0;
      while (X) {
        if (X.nodeType === f6) {
          var q = X.data;
          if (q === H9)
            if ($ === 0)
              return VW(X);
            else
              $--;
          else if (q === K9 || q === CW || q === BW)
            $++;
        }
        X = X.nextSibling;
      }
      return null;
    }
    function FA(Z) {
      var X = Z.previousSibling, $ = 0;
      while (X) {
        if (X.nodeType === f6) {
          var q = X.data;
          if (q === K9 || q === CW || q === BW)
            if ($ === 0)
              return X;
            else
              $--;
          else if (q === H9)
            $++;
        }
        X = X.previousSibling;
      }
      return null;
    }
    function tS(Z) {
      HW(Z);
    }
    function eS(Z) {
      HW(Z);
    }
    function QI(Z) {
      return Z !== "head" && Z !== "body";
    }
    function ZI(Z, X, $, q) {
      var H = !0;
      Y9(X.nodeValue, $, q, H);
    }
    function XI(Z, X, $, q, H, G) {
      if (X[W9] !== !0) {
        var E = !0;
        Y9(q.nodeValue, H, G, E);
      }
    }
    function JI(Z, X) {
      if (X.nodeType === SQ)
        _G(Z, X);
      else if (X.nodeType === f6)
        ;
      else
        TG(Z, X);
    }
    function $I(Z, X) {
      {
        var $ = Z.parentNode;
        if ($ !== null)
          if (X.nodeType === SQ)
            _G($, X);
          else if (X.nodeType === f6)
            ;
          else
            TG($, X);
      }
    }
    function YI(Z, X, $, q, H) {
      if (H || X[W9] !== !0)
        if (q.nodeType === SQ)
          _G($, q);
        else if (q.nodeType === f6)
          ;
        else
          TG($, q);
    }
    function qI(Z, X, $) {
      gG(Z, X);
    }
    function WI(Z, X) {
      xG(Z, X);
    }
    function KI(Z, X, $) {
      {
        var q = Z.parentNode;
        if (q !== null)
          gG(q, X);
      }
    }
    function HI(Z, X) {
      {
        var $ = Z.parentNode;
        if ($ !== null)
          xG($, X);
      }
    }
    function GI(Z, X, $, q, H, G) {
      if (G || X[W9] !== !0)
        gG($, q);
    }
    function zI(Z, X, $, q, H) {
      if (H || X[W9] !== !0)
        xG($, q);
    }
    function NI(Z) {
      K("An error occurred during hydration. The server HTML was replaced with client content in <%s>.", Z.nodeName.toLowerCase());
    }
    function EI(Z) {
      wW(Z);
    }
    var wY = Math.random().toString(36).slice(2), MY = "__reactFiber$" + wY, pG = "__reactProps$" + wY, SW = "__reactContainer$" + wY, dG = "__reactEvents$" + wY, FI = "__reactListeners$" + wY, UI = "__reactHandles$" + wY;
    function PI(Z) {
      delete Z[MY], delete Z[pG], delete Z[dG], delete Z[FI], delete Z[UI];
    }
    function IW(Z, X) {
      X[MY] = Z;
    }
    function z9(Z, X) {
      X[SW] = Z;
    }
    function UA(Z) {
      Z[SW] = null;
    }
    function _W(Z) {
      return !!Z[SW];
    }
    function q$(Z) {
      var X = Z[MY];
      if (X)
        return X;
      var $ = Z.parentNode;
      while ($) {
        if (X = $[SW] || $[MY], X) {
          var q = X.alternate;
          if (X.child !== null || q !== null && q.child !== null) {
            var H = FA(Z);
            while (H !== null) {
              var G = H[MY];
              if (G)
                return G;
              H = FA(H);
            }
          }
          return X;
        }
        Z = $, $ = Z.parentNode;
      }
      return null;
    }
    function l4(Z) {
      var X = Z[MY] || Z[SW];
      if (X)
        if (X.tag === R || X.tag === V || X.tag === l || X.tag === w)
          return X;
        else
          return null;
      return null;
    }
    function DY(Z) {
      if (Z.tag === R || Z.tag === V)
        return Z.stateNode;
      throw new Error("getNodeFromInstance: Invalid argument.");
    }
    function N9(Z) {
      return Z[pG] || null;
    }
    function lG(Z, X) {
      Z[pG] = X;
    }
    function AI(Z) {
      var X = Z[dG];
      if (X === void 0)
        X = Z[dG] = /* @__PURE__ */ new Set;
      return X;
    }
    var PA = {}, AA = Q.ReactDebugCurrentFrame;
    function E9(Z) {
      if (Z) {
        var X = Z._owner, $ = K0(Z.type, Z._source, X ? X.type : null);
        AA.setExtraStackFrame($);
      } else
        AA.setExtraStackFrame(null);
    }
    function dZ(Z, X, $, q, H) {
      {
        var G = Function.call.bind(Z0);
        for (var E in Z)
          if (G(Z, E)) {
            var U = void 0;
            try {
              if (typeof Z[E] !== "function") {
                var P = Error((q || "React class") + ": " + $ + " type `" + E + "` is invalid; it must be a function, usually from the `prop-types` package, but received `" + typeof Z[E] + "`.This often happens because of typos such as `PropTypes.function` instead of `PropTypes.func`.");
                throw P.name = "Invariant Violation", P;
              }
              U = Z[E](X, E, q, $, null, "SECRET_DO_NOT_PASS_THIS_OR_YOU_WILL_BE_FIRED");
            } catch (O) {
              U = O;
            }
            if (U && !(U instanceof Error))
              E9(H), K("%s: type specification of %s `%s` is invalid; the type checker function must return `null` or an `Error` but returned a %s. You may have forgotten to pass an argument to the type checker creator (arrayOf, instanceOf, objectOf, oneOf, oneOfType, and shape all require an argument).", q || "React class", $, E, typeof U), E9(null);
            if (U instanceof Error && !(U.message in PA))
              PA[U.message] = !0, E9(H), K("Failed %s type: %s", $, U.message), E9(null);
          }
      }
    }
    var nG = [], F9;
    F9 = [];
    var q4 = -1;
    function n4(Z) {
      return {
        current: Z
      };
    }
    function a8(Z, X) {
      if (q4 < 0) {
        K("Unexpected pop.");
        return;
      }
      if (X !== F9[q4])
        K("Unexpected Fiber popped.");
      Z.current = nG[q4], nG[q4] = null, F9[q4] = null, q4--;
    }
    function r8(Z, X, $) {
      q4++, nG[q4] = Z.current, F9[q4] = $, Z.current = X;
    }
    var LA = {}, rQ = {};
    Object.freeze(rQ);
    var W4 = n4(rQ), BX = n4(!1), sG = rQ;
    function kY(Z, X, $) {
      {
        if ($ && CX(X))
          return sG;
        return W4.current;
      }
    }
    function OA(Z, X, $) {
      {
        var q = Z.stateNode;
        q.__reactInternalMemoizedUnmaskedChildContext = X, q.__reactInternalMemoizedMaskedChildContext = $;
      }
    }
    function RY(Z, X) {
      {
        var $ = Z.type, q = $.contextTypes;
        if (!q)
          return rQ;
        var H = Z.stateNode;
        if (H && H.__reactInternalMemoizedUnmaskedChildContext === X)
          return H.__reactInternalMemoizedMaskedChildContext;
        var G = {};
        for (var E in q)
          G[E] = X[E];
        {
          var U = V0(Z) || "Unknown";
          dZ(q, G, "context", U);
        }
        if (H)
          OA(Z, X, G);
        return G;
      }
    }
    function U9() {
      return BX.current;
    }
    function CX(Z) {
      {
        var X = Z.childContextTypes;
        return X !== null && X !== void 0;
      }
    }
    function P9(Z) {
      a8(BX, Z), a8(W4, Z);
    }
    function oG(Z) {
      a8(BX, Z), a8(W4, Z);
    }
    function wA(Z, X, $) {
      {
        if (W4.current !== rQ)
          throw new Error("Unexpected context found on stack. This error is likely caused by a bug in React. Please file an issue.");
        r8(W4, X, Z), r8(BX, $, Z);
      }
    }
    function MA(Z, X, $) {
      {
        var q = Z.stateNode, H = X.childContextTypes;
        if (typeof q.getChildContext !== "function") {
          {
            var G = V0(Z) || "Unknown";
            if (!LA[G])
              LA[G] = !0, K("%s.childContextTypes is specified but there is no getChildContext() method on the instance. You can either define getChildContext() on %s or remove childContextTypes from it.", G, G);
          }
          return $;
        }
        var E = q.getChildContext();
        for (var U in E)
          if (!(U in H))
            throw new Error((V0(Z) || "Unknown") + '.getChildContext(): key "' + U + '" is not defined in childContextTypes.');
        {
          var P = V0(Z) || "Unknown";
          dZ(H, E, "child context", P);
        }
        return K1({}, $, E);
      }
    }
    function A9(Z) {
      {
        var X = Z.stateNode, $ = X && X.__reactInternalMemoizedMergedChildContext || rQ;
        return sG = W4.current, r8(W4, $, Z), r8(BX, BX.current, Z), !0;
      }
    }
    function DA(Z, X, $) {
      {
        var q = Z.stateNode;
        if (!q)
          throw new Error("Expected to have an instance by this point. This error is likely caused by a bug in React. Please file an issue.");
        if ($) {
          var H = MA(Z, X, sG);
          q.__reactInternalMemoizedMergedChildContext = H, a8(BX, Z), a8(W4, Z), r8(W4, H, Z), r8(BX, $, Z);
        } else
          a8(BX, Z), r8(BX, $, Z);
      }
    }
    function LI(Z) {
      {
        if (!QB(Z) || Z.tag !== F)
          throw new Error("Expected subtree parent to be a mounted class component. This error is likely caused by a bug in React. Please file an issue.");
        var X = Z;
        do {
          switch (X.tag) {
            case w:
              return X.stateNode.context;
            case F: {
              var $ = X.type;
              if (CX($))
                return X.stateNode.__reactInternalMemoizedMergedChildContext;
              break;
            }
          }
          X = X.return;
        } while (X !== null);
        throw new Error("Found unexpected detached subtree parent. This error is likely caused by a bug in React. Please file an issue.");
      }
    }
    var s4 = 0, L9 = 1, K4 = null, aG = !1, rG = !1;
    function kA(Z) {
      if (K4 === null)
        K4 = [Z];
      else
        K4.push(Z);
    }
    function OI(Z) {
      aG = !0, kA(Z);
    }
    function RA() {
      if (aG)
        o4();
    }
    function o4() {
      if (!rG && K4 !== null) {
        rG = !0;
        var Z = 0, X = pZ();
        try {
          var $ = !0, q = K4;
          P8(sQ);
          for (;Z < q.length; Z++) {
            var H = q[Z];
            do
              H = H($);
            while (H !== null);
          }
          K4 = null, aG = !1;
        } catch (G) {
          if (K4 !== null)
            K4 = K4.slice(Z + 1);
          throw sU(gK, o4), G;
        } finally {
          P8(X), rG = !1;
        }
      }
      return null;
    }
    var jY = [], BY = 0, O9 = null, w9 = 0, GZ = [], zZ = 0, W$ = null, H4 = 1, G4 = "";
    function wI(Z) {
      return H$(), (Z.flags & mU) !== S0;
    }
    function MI(Z) {
      return H$(), w9;
    }
    function DI() {
      var Z = G4, X = H4, $ = X & ~kI(X);
      return $.toString(32) + Z;
    }
    function K$(Z, X) {
      H$(), jY[BY++] = w9, jY[BY++] = O9, O9 = Z, w9 = X;
    }
    function jA(Z, X, $) {
      H$(), GZ[zZ++] = H4, GZ[zZ++] = G4, GZ[zZ++] = W$, W$ = Z;
      var q = H4, H = G4, G = M9(q) - 1, E = q & ~(1 << G), U = $ + 1, P = M9(X) + G;
      if (P > 30) {
        var O = G - G % 5, k = (1 << O) - 1, C = (E & k).toString(32), B = E >> O, v = G - O, h = M9(X) + v, f = U << v, q0 = f | B, k0 = C + H;
        H4 = 1 << h | q0, G4 = k0;
      } else {
        var w0 = U << G, N1 = w0 | E, E1 = H;
        H4 = 1 << P | N1, G4 = E1;
      }
    }
    function iG(Z) {
      H$();
      var X = Z.return;
      if (X !== null) {
        var $ = 1, q = 0;
        K$(Z, $), jA(Z, $, q);
      }
    }
    function M9(Z) {
      return 32 - eU(Z);
    }
    function kI(Z) {
      return 1 << M9(Z) - 1;
    }
    function tG(Z) {
      while (Z === O9)
        O9 = jY[--BY], jY[BY] = null, w9 = jY[--BY], jY[BY] = null;
      while (Z === W$)
        W$ = GZ[--zZ], GZ[zZ] = null, G4 = GZ[--zZ], GZ[zZ] = null, H4 = GZ[--zZ], GZ[zZ] = null;
    }
    function RI() {
      if (H$(), W$ !== null)
        return {
          id: H4,
          overflow: G4
        };
      else
        return null;
    }
    function jI(Z, X) {
      H$(), GZ[zZ++] = H4, GZ[zZ++] = G4, GZ[zZ++] = W$, H4 = X.id, G4 = X.overflow, W$ = Z;
    }
    function H$() {
      if (!S8())
        K("Expected to be hydrating. This is a bug in React. Please file an issue.");
    }
    var V8 = null, NZ = null, lZ = !1, G$ = !1, a4 = null;
    function BI() {
      if (lZ)
        K("We should not be hydrating here. This is a bug in React. Please file a bug.");
    }
    function BA() {
      G$ = !0;
    }
    function CI() {
      return G$;
    }
    function VI(Z) {
      var X = Z.stateNode.containerInfo;
      return NZ = nS(X), V8 = Z, lZ = !0, a4 = null, G$ = !1, !0;
    }
    function SI(Z, X, $) {
      if (NZ = sS(X), V8 = Z, lZ = !0, a4 = null, G$ = !1, $ !== null)
        jI(Z, $);
      return !0;
    }
    function CA(Z, X) {
      switch (Z.tag) {
        case w: {
          JI(Z.stateNode.containerInfo, X);
          break;
        }
        case R: {
          var $ = (Z.mode & A1) !== B0;
          YI(Z.type, Z.memoizedProps, Z.stateNode, X, $);
          break;
        }
        case l: {
          var q = Z.memoizedState;
          if (q.dehydrated !== null)
            $I(q.dehydrated, X);
          break;
        }
      }
    }
    function VA(Z, X) {
      CA(Z, X);
      var $ = yg();
      $.stateNode = X, $.return = Z;
      var q = Z.deletions;
      if (q === null)
        Z.deletions = [$], Z.flags |= sJ;
      else
        q.push($);
    }
    function eG(Z, X) {
      {
        if (G$)
          return;
        switch (Z.tag) {
          case w: {
            var $ = Z.stateNode.containerInfo;
            switch (X.tag) {
              case R:
                var { type: q, pendingProps: H } = X;
                qI($, q);
                break;
              case V:
                var G = X.pendingProps;
                WI($, G);
                break;
            }
            break;
          }
          case R: {
            var { type: E, memoizedProps: U, stateNode: P } = Z;
            switch (X.tag) {
              case R: {
                var { type: O, pendingProps: k } = X, C = (Z.mode & A1) !== B0;
                GI(E, U, P, O, k, C);
                break;
              }
              case V: {
                var B = X.pendingProps, v = (Z.mode & A1) !== B0;
                zI(E, U, P, B, v);
                break;
              }
            }
            break;
          }
          case l: {
            var h = Z.memoizedState, f = h.dehydrated;
            if (f !== null)
              switch (X.tag) {
                case R:
                  var { type: q0, pendingProps: k0 } = X;
                  KI(f, q0);
                  break;
                case V:
                  var w0 = X.pendingProps;
                  HI(f, w0);
                  break;
              }
            break;
          }
          default:
            return;
        }
      }
    }
    function SA(Z, X) {
      X.flags = X.flags & ~Q4 | m6, eG(Z, X);
    }
    function IA(Z, X) {
      switch (Z.tag) {
        case R: {
          var { type: $, pendingProps: q } = Z, H = bS(X, $);
          if (H !== null)
            return Z.stateNode = H, V8 = Z, NZ = lS(H), !0;
          return !1;
        }
        case V: {
          var G = Z.pendingProps, E = uS(X, G);
          if (E !== null)
            return Z.stateNode = E, V8 = Z, NZ = null, !0;
          return !1;
        }
        case l: {
          var U = cS(X);
          if (U !== null) {
            var P = {
              dehydrated: U,
              treeContext: RI(),
              retryLane: lQ
            };
            Z.memoizedState = P;
            var O = fg(U);
            return O.return = Z, Z.child = O, V8 = Z, NZ = null, !0;
          }
          return !1;
        }
        default:
          return !1;
      }
    }
    function Q2(Z) {
      return (Z.mode & A1) !== B0 && (Z.flags & I1) === S0;
    }
    function Z2(Z) {
      throw new Error("Hydration failed because the initial UI does not match what was rendered on the server.");
    }
    function X2(Z) {
      if (!lZ)
        return;
      var X = NZ;
      if (!X) {
        if (Q2(Z))
          eG(V8, Z), Z2();
        SA(V8, Z), lZ = !1, V8 = Z;
        return;
      }
      var $ = X;
      if (!IA(Z, X)) {
        if (Q2(Z))
          eG(V8, Z), Z2();
        X = VW($);
        var q = V8;
        if (!X || !IA(Z, X)) {
          SA(V8, Z), lZ = !1, V8 = Z;
          return;
        }
        VA(q, $);
      }
    }
    function II(Z, X, $) {
      var q = Z.stateNode, H = !G$, G = oS(q, Z.type, Z.memoizedProps, X, $, Z, H);
      if (Z.updateQueue = G, G !== null)
        return !0;
      return !1;
    }
    function _I(Z) {
      var { stateNode: X, memoizedProps: $ } = Z, q = aS(X, $, Z);
      if (q) {
        var H = V8;
        if (H !== null)
          switch (H.tag) {
            case w: {
              var G = H.stateNode.containerInfo, E = (H.mode & A1) !== B0;
              ZI(G, X, $, E);
              break;
            }
            case R: {
              var { type: U, memoizedProps: P, stateNode: O } = H, k = (H.mode & A1) !== B0;
              XI(U, P, O, X, $, k);
              break;
            }
          }
      }
      return q;
    }
    function TI(Z) {
      var X = Z.memoizedState, $ = X !== null ? X.dehydrated : null;
      if (!$)
        throw new Error("Expected to have a hydrated suspense instance. This error is likely caused by a bug in React. Please file an issue.");
      rS($, Z);
    }
    function gI(Z) {
      var X = Z.memoizedState, $ = X !== null ? X.dehydrated : null;
      if (!$)
        throw new Error("Expected to have a hydrated suspense instance. This error is likely caused by a bug in React. Please file an issue.");
      return iS($);
    }
    function _A(Z) {
      var X = Z.return;
      while (X !== null && X.tag !== R && X.tag !== w && X.tag !== l)
        X = X.return;
      V8 = X;
    }
    function D9(Z) {
      if (Z !== V8)
        return !1;
      if (!lZ)
        return _A(Z), lZ = !0, !1;
      if (Z.tag !== w && (Z.tag !== R || QI(Z.type) && !fG(Z.type, Z.memoizedProps))) {
        var X = NZ;
        if (X)
          if (Q2(Z))
            TA(Z), Z2();
          else
            while (X)
              VA(Z, X), X = VW(X);
      }
      if (_A(Z), Z.tag === l)
        NZ = gI(Z);
      else
        NZ = V8 ? VW(Z.stateNode) : null;
      return !0;
    }
    function xI() {
      return lZ && NZ !== null;
    }
    function TA(Z) {
      var X = NZ;
      while (X)
        CA(Z, X), X = VW(X);
    }
    function CY() {
      V8 = null, NZ = null, lZ = !1, G$ = !1;
    }
    function gA() {
      if (a4 !== null)
        CO(a4), a4 = null;
    }
    function S8() {
      return lZ;
    }
    function J2(Z) {
      if (a4 === null)
        a4 = [Z];
      else
        a4.push(Z);
    }
    var vI = Q.ReactCurrentBatchConfig, hI = null;
    function yI() {
      return vI.transition;
    }
    var nZ = {
      recordUnsafeLifecycleWarnings: function(Z, X) {},
      flushPendingUnsafeLifecycleWarnings: function() {},
      recordLegacyContextWarning: function(Z, X) {},
      flushLegacyContextWarning: function() {},
      discardPendingWarnings: function() {}
    };
    {
      var fI = function(Z) {
        var X = null, $ = Z;
        while ($ !== null) {
          if ($.mode & j6)
            X = $;
          $ = $.return;
        }
        return X;
      }, z$ = function(Z) {
        var X = [];
        return Z.forEach(function($) {
          X.push($);
        }), X.sort().join(", ");
      }, TW = [], gW = [], xW = [], vW = [], hW = [], yW = [], N$ = /* @__PURE__ */ new Set;
      nZ.recordUnsafeLifecycleWarnings = function(Z, X) {
        if (N$.has(Z.type))
          return;
        if (typeof X.componentWillMount === "function" && X.componentWillMount.__suppressDeprecationWarning !== !0)
          TW.push(Z);
        if (Z.mode & j6 && typeof X.UNSAFE_componentWillMount === "function")
          gW.push(Z);
        if (typeof X.componentWillReceiveProps === "function" && X.componentWillReceiveProps.__suppressDeprecationWarning !== !0)
          xW.push(Z);
        if (Z.mode & j6 && typeof X.UNSAFE_componentWillReceiveProps === "function")
          vW.push(Z);
        if (typeof X.componentWillUpdate === "function" && X.componentWillUpdate.__suppressDeprecationWarning !== !0)
          hW.push(Z);
        if (Z.mode & j6 && typeof X.UNSAFE_componentWillUpdate === "function")
          yW.push(Z);
      }, nZ.flushPendingUnsafeLifecycleWarnings = function() {
        var Z = /* @__PURE__ */ new Set;
        if (TW.length > 0)
          TW.forEach(function(B) {
            Z.add(V0(B) || "Component"), N$.add(B.type);
          }), TW = [];
        var X = /* @__PURE__ */ new Set;
        if (gW.length > 0)
          gW.forEach(function(B) {
            X.add(V0(B) || "Component"), N$.add(B.type);
          }), gW = [];
        var $ = /* @__PURE__ */ new Set;
        if (xW.length > 0)
          xW.forEach(function(B) {
            $.add(V0(B) || "Component"), N$.add(B.type);
          }), xW = [];
        var q = /* @__PURE__ */ new Set;
        if (vW.length > 0)
          vW.forEach(function(B) {
            q.add(V0(B) || "Component"), N$.add(B.type);
          }), vW = [];
        var H = /* @__PURE__ */ new Set;
        if (hW.length > 0)
          hW.forEach(function(B) {
            H.add(V0(B) || "Component"), N$.add(B.type);
          }), hW = [];
        var G = /* @__PURE__ */ new Set;
        if (yW.length > 0)
          yW.forEach(function(B) {
            G.add(V0(B) || "Component"), N$.add(B.type);
          }), yW = [];
        if (X.size > 0) {
          var E = z$(X);
          K(`Using UNSAFE_componentWillMount in strict mode is not recommended and may indicate bugs in your code. See https://reactjs.org/link/unsafe-component-lifecycles for details.

* Move code with side effects to componentDidMount, and set initial state in the constructor.

Please update the following components: %s`, E);
        }
        if (q.size > 0) {
          var U = z$(q);
          K(`Using UNSAFE_componentWillReceiveProps in strict mode is not recommended and may indicate bugs in your code. See https://reactjs.org/link/unsafe-component-lifecycles for details.

* Move data fetching code or side effects to componentDidUpdate.
* If you're updating state whenever props change, refactor your code to use memoization techniques or move it to static getDerivedStateFromProps. Learn more at: https://reactjs.org/link/derived-state

Please update the following components: %s`, U);
        }
        if (G.size > 0) {
          var P = z$(G);
          K(`Using UNSAFE_componentWillUpdate in strict mode is not recommended and may indicate bugs in your code. See https://reactjs.org/link/unsafe-component-lifecycles for details.

* Move data fetching code or side effects to componentDidUpdate.

Please update the following components: %s`, P);
        }
        if (Z.size > 0) {
          var O = z$(Z);
          W(`componentWillMount has been renamed, and is not recommended for use. See https://reactjs.org/link/unsafe-component-lifecycles for details.

* Move code with side effects to componentDidMount, and set initial state in the constructor.
* Rename componentWillMount to UNSAFE_componentWillMount to suppress this warning in non-strict mode. In React 18.x, only the UNSAFE_ name will work. To rename all deprecated lifecycles to their new names, you can run \`npx react-codemod rename-unsafe-lifecycles\` in your project source folder.

Please update the following components: %s`, O);
        }
        if ($.size > 0) {
          var k = z$($);
          W(`componentWillReceiveProps has been renamed, and is not recommended for use. See https://reactjs.org/link/unsafe-component-lifecycles for details.

* Move data fetching code or side effects to componentDidUpdate.
* If you're updating state whenever props change, refactor your code to use memoization techniques or move it to static getDerivedStateFromProps. Learn more at: https://reactjs.org/link/derived-state
* Rename componentWillReceiveProps to UNSAFE_componentWillReceiveProps to suppress this warning in non-strict mode. In React 18.x, only the UNSAFE_ name will work. To rename all deprecated lifecycles to their new names, you can run \`npx react-codemod rename-unsafe-lifecycles\` in your project source folder.

Please update the following components: %s`, k);
        }
        if (H.size > 0) {
          var C = z$(H);
          W(`componentWillUpdate has been renamed, and is not recommended for use. See https://reactjs.org/link/unsafe-component-lifecycles for details.

* Move data fetching code or side effects to componentDidUpdate.
* Rename componentWillUpdate to UNSAFE_componentWillUpdate to suppress this warning in non-strict mode. In React 18.x, only the UNSAFE_ name will work. To rename all deprecated lifecycles to their new names, you can run \`npx react-codemod rename-unsafe-lifecycles\` in your project source folder.

Please update the following components: %s`, C);
        }
      };
      var k9 = /* @__PURE__ */ new Map, xA = /* @__PURE__ */ new Set;
      nZ.recordLegacyContextWarning = function(Z, X) {
        var $ = fI(Z);
        if ($ === null) {
          K("Expected to find a StrictMode component in a strict mode tree. This error is likely caused by a bug in React. Please file an issue.");
          return;
        }
        if (xA.has(Z.type))
          return;
        var q = k9.get($);
        if (Z.type.contextTypes != null || Z.type.childContextTypes != null || X !== null && typeof X.getChildContext === "function") {
          if (q === void 0)
            q = [], k9.set($, q);
          q.push(Z);
        }
      }, nZ.flushLegacyContextWarning = function() {
        k9.forEach(function(Z, X) {
          if (Z.length === 0)
            return;
          var $ = Z[0], q = /* @__PURE__ */ new Set;
          Z.forEach(function(G) {
            q.add(V0(G) || "Component"), xA.add(G.type);
          });
          var H = z$(q);
          try {
            w6($), K(`Legacy context API has been detected within a strict-mode tree.

The old API will be supported in all 16.x releases, but applications using it should migrate to the new version.

Please update the following components: %s

Learn more about this warning here: https://reactjs.org/link/legacy-context`, H);
          } finally {
            N8();
          }
        });
      }, nZ.discardPendingWarnings = function() {
        TW = [], gW = [], xW = [], vW = [], hW = [], yW = [], k9 = /* @__PURE__ */ new Map;
      };
    }
    var $2, Y2, q2, W2, K2, vA = function(Z, X) {};
    $2 = !1, Y2 = !1, q2 = {}, W2 = {}, K2 = {}, vA = function(Z, X) {
      if (Z === null || typeof Z !== "object")
        return;
      if (!Z._store || Z._store.validated || Z.key != null)
        return;
      if (typeof Z._store !== "object")
        throw new Error("React Component in warnForMissingKey should have a _store. This error is likely caused by a bug in React. Please file an issue.");
      Z._store.validated = !0;
      var $ = V0(X) || "Component";
      if (W2[$])
        return;
      W2[$] = !0, K('Each child in a list should have a unique "key" prop. See https://reactjs.org/link/warning-keys for more information.');
    };
    function mI(Z) {
      return Z.prototype && Z.prototype.isReactComponent;
    }
    function fW(Z, X, $) {
      var q = $.ref;
      if (q !== null && typeof q !== "function" && typeof q !== "object") {
        if ((Z.mode & j6 || U1) && !($._owner && $._self && $._owner.stateNode !== $._self) && !($._owner && $._owner.tag !== F) && !(typeof $.type === "function" && !mI($.type)) && $._owner) {
          var H = V0(Z) || "Component";
          if (!q2[H])
            K('Component "%s" contains the string ref "%s". Support for string refs will be removed in a future major release. We recommend using useRef() or createRef() instead. Learn more about using refs safely here: https://reactjs.org/link/strict-mode-string-ref', H, q), q2[H] = !0;
        }
        if ($._owner) {
          var G = $._owner, E;
          if (G) {
            var U = G;
            if (U.tag !== F)
              throw new Error("Function components cannot have string refs. We recommend using useRef() instead. Learn more about using refs safely here: https://reactjs.org/link/strict-mode-string-ref");
            E = U.stateNode;
          }
          if (!E)
            throw new Error("Missing owner for string ref " + q + ". This error is likely caused by a bug in React. Please file an issue.");
          var P = E;
          p6(q, "ref");
          var O = "" + q;
          if (X !== null && X.ref !== null && typeof X.ref === "function" && X.ref._stringRef === O)
            return X.ref;
          var k = function(C) {
            var B = P.refs;
            if (C === null)
              delete B[O];
            else
              B[O] = C;
          };
          return k._stringRef = O, k;
        } else {
          if (typeof q !== "string")
            throw new Error("Expected ref to be a function, a string, an object returned by React.createRef(), or null.");
          if (!$._owner)
            throw new Error("Element ref was specified as a string (" + q + `) but no owner was set. This could happen for one of the following reasons:
1. You may be adding a ref to a function component
2. You may be adding a ref to a component that was not created inside a component's render method
3. You have multiple copies of React loaded
See https://reactjs.org/link/refs-must-have-owner for more information.`);
        }
      }
      return q;
    }
    function R9(Z, X) {
      var $ = Object.prototype.toString.call(X);
      throw new Error("Objects are not valid as a React child (found: " + ($ === "[object Object]" ? "object with keys {" + Object.keys(X).join(", ") + "}" : $) + "). If you meant to render a collection of children, use an array instead.");
    }
    function j9(Z) {
      {
        var X = V0(Z) || "Component";
        if (K2[X])
          return;
        K2[X] = !0, K("Functions are not valid as a React child. This may happen if you return a Component instead of <Component /> from render. Or maybe you meant to call this function rather than return it.");
      }
    }
    function hA(Z) {
      var { _payload: X, _init: $ } = Z;
      return $(X);
    }
    function yA(Z) {
      function X(_, b) {
        if (!Z)
          return;
        var T = _.deletions;
        if (T === null)
          _.deletions = [b], _.flags |= sJ;
        else
          T.push(b);
      }
      function $(_, b) {
        if (!Z)
          return null;
        var T = b;
        while (T !== null)
          X(_, T), T = T.sibling;
        return null;
      }
      function q(_, b) {
        var T = /* @__PURE__ */ new Map, a = b;
        while (a !== null) {
          if (a.key !== null)
            T.set(a.key, a);
          else
            T.set(a.index, a);
          a = a.sibling;
        }
        return T;
      }
      function H(_, b) {
        var T = M$(_, b);
        return T.index = 0, T.sibling = null, T;
      }
      function G(_, b, T) {
        if (_.index = T, !Z)
          return _.flags |= mU, b;
        var a = _.alternate;
        if (a !== null) {
          var E0 = a.index;
          if (E0 < b)
            return _.flags |= m6, b;
          else
            return E0;
        } else
          return _.flags |= m6, b;
      }
      function E(_) {
        if (Z && _.alternate === null)
          _.flags |= m6;
        return _;
      }
      function U(_, b, T, a) {
        if (b === null || b.tag !== V) {
          var E0 = YN(T, _.mode, a);
          return E0.return = _, E0;
        } else {
          var H0 = H(b, T);
          return H0.return = _, H0;
        }
      }
      function P(_, b, T, a) {
        var E0 = T.type;
        if (E0 === KQ)
          return k(_, b, T.props.children, a, T.key);
        if (b !== null) {
          if (b.elementType === E0 || pO(b, T) || typeof E0 === "object" && E0 !== null && E0.$$typeof === n6 && hA(E0) === b.type) {
            var H0 = H(b, T.props);
            return H0.ref = fW(_, b, T), H0.return = _, H0._debugSource = T._source, H0._debugOwner = T._owner, H0;
          }
        }
        var g0 = $N(T, _.mode, a);
        return g0.ref = fW(_, b, T), g0.return = _, g0;
      }
      function O(_, b, T, a) {
        if (b === null || b.tag !== D || b.stateNode.containerInfo !== T.containerInfo || b.stateNode.implementation !== T.implementation) {
          var E0 = qN(T, _.mode, a);
          return E0.return = _, E0;
        } else {
          var H0 = H(b, T.children || []);
          return H0.return = _, H0;
        }
      }
      function k(_, b, T, a, E0) {
        if (b === null || b.tag !== g) {
          var H0 = qJ(T, _.mode, a, E0);
          return H0.return = _, H0;
        } else {
          var g0 = H(b, T);
          return g0.return = _, g0;
        }
      }
      function C(_, b, T) {
        if (typeof b === "string" && b !== "" || typeof b === "number") {
          var a = YN("" + b, _.mode, T);
          return a.return = _, a;
        }
        if (typeof b === "object" && b !== null) {
          switch (b.$$typeof) {
            case s8: {
              var E0 = $N(b, _.mode, T);
              return E0.ref = fW(_, null, b), E0.return = _, E0;
            }
            case o8: {
              var H0 = qN(b, _.mode, T);
              return H0.return = _, H0;
            }
            case n6: {
              var { _payload: g0, _init: p0 } = b;
              return C(_, p0(g0), T);
            }
          }
          if (S1(b) || mZ(b)) {
            var c1 = qJ(b, _.mode, T, null);
            return c1.return = _, c1;
          }
          R9(_, b);
        }
        if (typeof b === "function")
          j9(_);
        return null;
      }
      function B(_, b, T, a) {
        var E0 = b !== null ? b.key : null;
        if (typeof T === "string" && T !== "" || typeof T === "number") {
          if (E0 !== null)
            return null;
          return U(_, b, "" + T, a);
        }
        if (typeof T === "object" && T !== null) {
          switch (T.$$typeof) {
            case s8:
              if (T.key === E0)
                return P(_, b, T, a);
              else
                return null;
            case o8:
              if (T.key === E0)
                return O(_, b, T, a);
              else
                return null;
            case n6: {
              var { _payload: H0, _init: g0 } = T;
              return B(_, b, g0(H0), a);
            }
          }
          if (S1(T) || mZ(T)) {
            if (E0 !== null)
              return null;
            return k(_, b, T, a, null);
          }
          R9(_, T);
        }
        if (typeof T === "function")
          j9(_);
        return null;
      }
      function v(_, b, T, a, E0) {
        if (typeof a === "string" && a !== "" || typeof a === "number") {
          var H0 = _.get(T) || null;
          return U(b, H0, "" + a, E0);
        }
        if (typeof a === "object" && a !== null) {
          switch (a.$$typeof) {
            case s8: {
              var g0 = _.get(a.key === null ? T : a.key) || null;
              return P(b, g0, a, E0);
            }
            case o8: {
              var p0 = _.get(a.key === null ? T : a.key) || null;
              return O(b, p0, a, E0);
            }
            case n6:
              var { _payload: c1, _init: R1 } = a;
              return v(_, b, T, R1(c1), E0);
          }
          if (S1(a) || mZ(a)) {
            var S6 = _.get(T) || null;
            return k(b, S6, a, E0, null);
          }
          R9(b, a);
        }
        if (typeof a === "function")
          j9(b);
        return null;
      }
      function h(_, b, T) {
        {
          if (typeof _ !== "object" || _ === null)
            return b;
          switch (_.$$typeof) {
            case s8:
            case o8:
              vA(_, T);
              var a = _.key;
              if (typeof a !== "string")
                break;
              if (b === null) {
                b = /* @__PURE__ */ new Set, b.add(a);
                break;
              }
              if (!b.has(a)) {
                b.add(a);
                break;
              }
              K("Encountered two children with the same key, `%s`. Keys should be unique so that components maintain their identity across updates. Non-unique keys may cause children to be " + "duplicated and/or omitted — the behavior is unsupported and " + "could change in a future version.", a);
              break;
            case n6:
              var { _payload: E0, _init: H0 } = _;
              h(H0(E0), b, T);
              break;
          }
        }
        return b;
      }
      function f(_, b, T, a) {
        {
          var E0 = null;
          for (var H0 = 0;H0 < T.length; H0++) {
            var g0 = T[H0];
            E0 = h(g0, E0, _);
          }
        }
        var p0 = null, c1 = null, R1 = b, S6 = 0, j1 = 0, B6 = null;
        for (;R1 !== null && j1 < T.length; j1++) {
          if (R1.index > j1)
            B6 = R1, R1 = null;
          else
            B6 = R1.sibling;
          var t8 = B(_, R1, T[j1], a);
          if (t8 === null) {
            if (R1 === null)
              R1 = B6;
            break;
          }
          if (Z) {
            if (R1 && t8.alternate === null)
              X(_, R1);
          }
          if (S6 = G(t8, S6, j1), c1 === null)
            p0 = t8;
          else
            c1.sibling = t8;
          c1 = t8, R1 = B6;
        }
        if (j1 === T.length) {
          if ($(_, R1), S8()) {
            var h8 = j1;
            K$(_, h8);
          }
          return p0;
        }
        if (R1 === null) {
          for (;j1 < T.length; j1++) {
            var tQ = C(_, T[j1], a);
            if (tQ === null)
              continue;
            if (S6 = G(tQ, S6, j1), c1 === null)
              p0 = tQ;
            else
              c1.sibling = tQ;
            c1 = tQ;
          }
          if (S8()) {
            var PQ = j1;
            K$(_, PQ);
          }
          return p0;
        }
        var AQ = q(_, R1);
        for (;j1 < T.length; j1++) {
          var e8 = v(AQ, _, j1, T[j1], a);
          if (e8 !== null) {
            if (Z) {
              if (e8.alternate !== null)
                AQ.delete(e8.key === null ? j1 : e8.key);
            }
            if (S6 = G(e8, S6, j1), c1 === null)
              p0 = e8;
            else
              c1.sibling = e8;
            c1 = e8;
          }
        }
        if (Z)
          AQ.forEach(function(nY) {
            return X(_, nY);
          });
        if (S8()) {
          var A4 = j1;
          K$(_, A4);
        }
        return p0;
      }
      function q0(_, b, T, a) {
        var E0 = mZ(T);
        if (typeof E0 !== "function")
          throw new Error("An object is not an iterable. This error is likely caused by a bug in React. Please file an issue.");
        {
          if (typeof Symbol === "function" && T[Symbol.toStringTag] === "Generator") {
            if (!Y2)
              K("Using Generators as children is unsupported and will likely yield unexpected results because enumerating a generator mutates it. You may convert it to an array with `Array.from()` or the `[...spread]` operator before rendering. Keep in mind you might need to polyfill these features for older browsers.");
            Y2 = !0;
          }
          if (T.entries === E0) {
            if (!$2)
              K("Using Maps as children is not supported. Use an array of keyed ReactElements instead.");
            $2 = !0;
          }
          var H0 = E0.call(T);
          if (H0) {
            var g0 = null, p0 = H0.next();
            for (;!p0.done; p0 = H0.next()) {
              var c1 = p0.value;
              g0 = h(c1, g0, _);
            }
          }
        }
        var R1 = E0.call(T);
        if (R1 == null)
          throw new Error("An iterable object provided no iterator.");
        var S6 = null, j1 = null, B6 = b, t8 = 0, h8 = 0, tQ = null, PQ = R1.next();
        for (;B6 !== null && !PQ.done; h8++, PQ = R1.next()) {
          if (B6.index > h8)
            tQ = B6, B6 = null;
          else
            tQ = B6.sibling;
          var AQ = B(_, B6, PQ.value, a);
          if (AQ === null) {
            if (B6 === null)
              B6 = tQ;
            break;
          }
          if (Z) {
            if (B6 && AQ.alternate === null)
              X(_, B6);
          }
          if (t8 = G(AQ, t8, h8), j1 === null)
            S6 = AQ;
          else
            j1.sibling = AQ;
          j1 = AQ, B6 = tQ;
        }
        if (PQ.done) {
          if ($(_, B6), S8()) {
            var e8 = h8;
            K$(_, e8);
          }
          return S6;
        }
        if (B6 === null) {
          for (;!PQ.done; h8++, PQ = R1.next()) {
            var A4 = C(_, PQ.value, a);
            if (A4 === null)
              continue;
            if (t8 = G(A4, t8, h8), j1 === null)
              S6 = A4;
            else
              j1.sibling = A4;
            j1 = A4;
          }
          if (S8()) {
            var nY = h8;
            K$(_, nY);
          }
          return S6;
        }
        var P3 = q(_, B6);
        for (;!PQ.done; h8++, PQ = R1.next()) {
          var vX = v(P3, _, h8, PQ.value, a);
          if (vX !== null) {
            if (Z) {
              if (vX.alternate !== null)
                P3.delete(vX.key === null ? h8 : vX.key);
            }
            if (t8 = G(vX, t8, h8), j1 === null)
              S6 = vX;
            else
              j1.sibling = vX;
            j1 = vX;
          }
        }
        if (Z)
          P3.forEach(function(Ux) {
            return X(_, Ux);
          });
        if (S8()) {
          var Fx = h8;
          K$(_, Fx);
        }
        return S6;
      }
      function k0(_, b, T, a) {
        if (b !== null && b.tag === V) {
          $(_, b.sibling);
          var E0 = H(b, T);
          return E0.return = _, E0;
        }
        $(_, b);
        var H0 = YN(T, _.mode, a);
        return H0.return = _, H0;
      }
      function w0(_, b, T, a) {
        var E0 = T.key, H0 = b;
        while (H0 !== null) {
          if (H0.key === E0) {
            var g0 = T.type;
            if (g0 === KQ) {
              if (H0.tag === g) {
                $(_, H0.sibling);
                var p0 = H(H0, T.props.children);
                return p0.return = _, p0._debugSource = T._source, p0._debugOwner = T._owner, p0;
              }
            } else if (H0.elementType === g0 || pO(H0, T) || typeof g0 === "object" && g0 !== null && g0.$$typeof === n6 && hA(g0) === H0.type) {
              $(_, H0.sibling);
              var c1 = H(H0, T.props);
              return c1.ref = fW(_, H0, T), c1.return = _, c1._debugSource = T._source, c1._debugOwner = T._owner, c1;
            }
            $(_, H0);
            break;
          } else
            X(_, H0);
          H0 = H0.sibling;
        }
        if (T.type === KQ) {
          var R1 = qJ(T.props.children, _.mode, a, T.key);
          return R1.return = _, R1;
        } else {
          var S6 = $N(T, _.mode, a);
          return S6.ref = fW(_, b, T), S6.return = _, S6;
        }
      }
      function N1(_, b, T, a) {
        var E0 = T.key, H0 = b;
        while (H0 !== null) {
          if (H0.key === E0)
            if (H0.tag === D && H0.stateNode.containerInfo === T.containerInfo && H0.stateNode.implementation === T.implementation) {
              $(_, H0.sibling);
              var g0 = H(H0, T.children || []);
              return g0.return = _, g0;
            } else {
              $(_, H0);
              break;
            }
          else
            X(_, H0);
          H0 = H0.sibling;
        }
        var p0 = qN(T, _.mode, a);
        return p0.return = _, p0;
      }
      function E1(_, b, T, a) {
        var E0 = typeof T === "object" && T !== null && T.type === KQ && T.key === null;
        if (E0)
          T = T.props.children;
        if (typeof T === "object" && T !== null) {
          switch (T.$$typeof) {
            case s8:
              return E(w0(_, b, T, a));
            case o8:
              return E(N1(_, b, T, a));
            case n6:
              var { _payload: H0, _init: g0 } = T;
              return E1(_, b, g0(H0), a);
          }
          if (S1(T))
            return f(_, b, T, a);
          if (mZ(T))
            return q0(_, b, T, a);
          R9(_, T);
        }
        if (typeof T === "string" && T !== "" || typeof T === "number")
          return E(k0(_, b, "" + T, a));
        if (typeof T === "function")
          j9(_);
        return $(_, b);
      }
      return E1;
    }
    var VY = yA(!0), fA = yA(!1);
    function bI(Z, X) {
      if (Z !== null && X.child !== Z.child)
        throw new Error("Resuming work not yet implemented.");
      if (X.child === null)
        return;
      var $ = X.child, q = M$($, $.pendingProps);
      X.child = q, q.return = X;
      while ($.sibling !== null)
        $ = $.sibling, q = q.sibling = M$($, $.pendingProps), q.return = X;
      q.sibling = null;
    }
    function uI(Z, X) {
      var $ = Z.child;
      while ($ !== null)
        Tg($, X), $ = $.sibling;
    }
    var H2 = n4(null), G2;
    G2 = {};
    var B9 = null, SY = null, z2 = null, C9 = !1;
    function V9() {
      B9 = null, SY = null, z2 = null, C9 = !1;
    }
    function mA() {
      C9 = !0;
    }
    function bA() {
      C9 = !1;
    }
    function uA(Z, X, $) {
      {
        r8(H2, X._currentValue, Z), X._currentValue = $;
        {
          if (X._currentRenderer !== void 0 && X._currentRenderer !== null && X._currentRenderer !== G2)
            K("Detected multiple renderers concurrently rendering the same context provider. This is currently unsupported.");
          X._currentRenderer = G2;
        }
      }
    }
    function N2(Z, X) {
      var $ = H2.current;
      a8(H2, X), Z._currentValue = $;
    }
    function E2(Z, X, $) {
      var q = Z;
      while (q !== null) {
        var H = q.alternate;
        if (!EY(q.childLanes, X)) {
          if (q.childLanes = Q1(q.childLanes, X), H !== null)
            H.childLanes = Q1(H.childLanes, X);
        } else if (H !== null && !EY(H.childLanes, X))
          H.childLanes = Q1(H.childLanes, X);
        if (q === $)
          break;
        q = q.return;
      }
      if (q !== $)
        K("Expected to find the propagation root when scheduling context work. This error is likely caused by a bug in React. Please file an issue.");
    }
    function cI(Z, X, $) {
      pI(Z, X, $);
    }
    function pI(Z, X, $) {
      var q = Z.child;
      if (q !== null)
        q.return = Z;
      while (q !== null) {
        var H = void 0, G = q.dependencies;
        if (G !== null) {
          H = q.child;
          var E = G.firstContext;
          while (E !== null) {
            if (E.context === X) {
              if (q.tag === F) {
                var U = XW($), P = z4(J6, U);
                P.tag = I9;
                var O = q.updateQueue;
                if (O === null)
                  ;
                else {
                  var k = O.shared, C = k.pending;
                  if (C === null)
                    P.next = P;
                  else
                    P.next = C.next, C.next = P;
                  k.pending = P;
                }
              }
              q.lanes = Q1(q.lanes, $);
              var B = q.alternate;
              if (B !== null)
                B.lanes = Q1(B.lanes, $);
              E2(q.return, $, Z), G.lanes = Q1(G.lanes, $);
              break;
            }
            E = E.next;
          }
        } else if (q.tag === F0)
          H = q.type === Z.type ? null : q.child;
        else if (q.tag === I0) {
          var v = q.return;
          if (v === null)
            throw new Error("We just came from a parent so we must have had a parent. This is a bug in React.");
          v.lanes = Q1(v.lanes, $);
          var h = v.alternate;
          if (h !== null)
            h.lanes = Q1(h.lanes, $);
          E2(v, $, Z), H = q.sibling;
        } else
          H = q.child;
        if (H !== null)
          H.return = q;
        else {
          H = q;
          while (H !== null) {
            if (H === Z) {
              H = null;
              break;
            }
            var f = H.sibling;
            if (f !== null) {
              f.return = H.return, H = f;
              break;
            }
            H = H.return;
          }
        }
        q = H;
      }
    }
    function IY(Z, X) {
      B9 = Z, SY = null, z2 = null;
      var $ = Z.dependencies;
      if ($ !== null) {
        var q = $.firstContext;
        if (q !== null) {
          if (nQ($.lanes, X))
            eW();
          $.firstContext = null;
        }
      }
    }
    function b6(Z) {
      if (C9)
        K("Context can only be read while React is rendering. In classes, you can read it in the render method or getDerivedStateFromProps. In function components, you can read it directly in the function body, but not inside Hooks like useReducer() or useMemo().");
      var X = Z._currentValue;
      if (z2 === Z)
        ;
      else {
        var $ = {
          context: Z,
          memoizedValue: X,
          next: null
        };
        if (SY === null) {
          if (B9 === null)
            throw new Error("Context can only be read while React is rendering. In classes, you can read it in the render method or getDerivedStateFromProps. In function components, you can read it directly in the function body, but not inside Hooks like useReducer() or useMemo().");
          SY = $, B9.dependencies = {
            lanes: n,
            firstContext: $
          };
        } else
          SY = SY.next = $;
      }
      return X;
    }
    var E$ = null;
    function F2(Z) {
      if (E$ === null)
        E$ = [Z];
      else
        E$.push(Z);
    }
    function dI() {
      if (E$ !== null) {
        for (var Z = 0;Z < E$.length; Z++) {
          var X = E$[Z], $ = X.interleaved;
          if ($ !== null) {
            X.interleaved = null;
            var q = $.next, H = X.pending;
            if (H !== null) {
              var G = H.next;
              H.next = q, $.next = G;
            }
            X.pending = $;
          }
        }
        E$ = null;
      }
    }
    function cA(Z, X, $, q) {
      var H = X.interleaved;
      if (H === null)
        $.next = $, F2(X);
      else
        $.next = H.next, H.next = $;
      return X.interleaved = $, S9(Z, q);
    }
    function lI(Z, X, $, q) {
      var H = X.interleaved;
      if (H === null)
        $.next = $, F2(X);
      else
        $.next = H.next, H.next = $;
      X.interleaved = $;
    }
    function nI(Z, X, $, q) {
      var H = X.interleaved;
      if (H === null)
        $.next = $, F2(X);
      else
        $.next = H.next, H.next = $;
      return X.interleaved = $, S9(Z, q);
    }
    function _Q(Z, X) {
      return S9(Z, X);
    }
    var sI = S9;
    function S9(Z, X) {
      Z.lanes = Q1(Z.lanes, X);
      var $ = Z.alternate;
      if ($ !== null)
        $.lanes = Q1($.lanes, X);
      if ($ === null && (Z.flags & (m6 | Q4)) !== S0)
        mO(Z);
      var q = Z, H = Z.return;
      while (H !== null) {
        if (H.childLanes = Q1(H.childLanes, X), $ = H.alternate, $ !== null)
          $.childLanes = Q1($.childLanes, X);
        else if ((H.flags & (m6 | Q4)) !== S0)
          mO(Z);
        q = H, H = H.return;
      }
      if (q.tag === w) {
        var G = q.stateNode;
        return G;
      } else
        return null;
    }
    var pA = 0, dA = 1, I9 = 2, U2 = 3, _9 = !1, P2, T9;
    P2 = !1, T9 = null;
    function A2(Z) {
      var X = {
        baseState: Z.memoizedState,
        firstBaseUpdate: null,
        lastBaseUpdate: null,
        shared: {
          pending: null,
          interleaved: null,
          lanes: n
        },
        effects: null
      };
      Z.updateQueue = X;
    }
    function lA(Z, X) {
      var $ = X.updateQueue, q = Z.updateQueue;
      if ($ === q) {
        var H = {
          baseState: q.baseState,
          firstBaseUpdate: q.firstBaseUpdate,
          lastBaseUpdate: q.lastBaseUpdate,
          shared: q.shared,
          effects: q.effects
        };
        X.updateQueue = H;
      }
    }
    function z4(Z, X) {
      var $ = {
        eventTime: Z,
        lane: X,
        tag: pA,
        payload: null,
        callback: null,
        next: null
      };
      return $;
    }
    function r4(Z, X, $) {
      var q = Z.updateQueue;
      if (q === null)
        return null;
      var H = q.shared;
      if (T9 === H && !P2)
        K("An update (setState, replaceState, or forceUpdate) was scheduled from inside an update function. Update functions should be pure, with zero side-effects. Consider using componentDidUpdate or a callback."), P2 = !0;
      if (aT()) {
        var G = H.pending;
        if (G === null)
          X.next = X;
        else
          X.next = G.next, G.next = X;
        return H.pending = X, sI(Z, $);
      } else
        return nI(Z, H, X, $);
    }
    function g9(Z, X, $) {
      var q = X.updateQueue;
      if (q === null)
        return;
      var H = q.shared;
      if (JP($)) {
        var G = H.lanes;
        G = YP(G, Z.pendingLanes);
        var E = Q1(G, $);
        H.lanes = E, HG(Z, E);
      }
    }
    function L2(Z, X) {
      var { updateQueue: $, alternate: q } = Z;
      if (q !== null) {
        var H = q.updateQueue;
        if ($ === H) {
          var G = null, E = null, U = $.firstBaseUpdate;
          if (U !== null) {
            var P = U;
            do {
              var O = {
                eventTime: P.eventTime,
                lane: P.lane,
                tag: P.tag,
                payload: P.payload,
                callback: P.callback,
                next: null
              };
              if (E === null)
                G = E = O;
              else
                E.next = O, E = O;
              P = P.next;
            } while (P !== null);
            if (E === null)
              G = E = X;
            else
              E.next = X, E = X;
          } else
            G = E = X;
          $ = {
            baseState: H.baseState,
            firstBaseUpdate: G,
            lastBaseUpdate: E,
            shared: H.shared,
            effects: H.effects
          }, Z.updateQueue = $;
          return;
        }
      }
      var k = $.lastBaseUpdate;
      if (k === null)
        $.firstBaseUpdate = X;
      else
        k.next = X;
      $.lastBaseUpdate = X;
    }
    function oI(Z, X, $, q, H, G) {
      switch ($.tag) {
        case dA: {
          var E = $.payload;
          if (typeof E === "function") {
            mA();
            var U = E.call(G, q, H);
            {
              if (Z.mode & j6) {
                F8(!0);
                try {
                  E.call(G, q, H);
                } finally {
                  F8(!1);
                }
              }
              bA();
            }
            return U;
          }
          return E;
        }
        case U2:
          Z.flags = Z.flags & ~NQ | I1;
        case pA: {
          var P = $.payload, O;
          if (typeof P === "function") {
            mA(), O = P.call(G, q, H);
            {
              if (Z.mode & j6) {
                F8(!0);
                try {
                  P.call(G, q, H);
                } finally {
                  F8(!1);
                }
              }
              bA();
            }
          } else
            O = P;
          if (O === null || O === void 0)
            return q;
          return K1({}, q, O);
        }
        case I9:
          return _9 = !0, q;
      }
      return q;
    }
    function x9(Z, X, $, q) {
      var H = Z.updateQueue;
      _9 = !1, T9 = H.shared;
      var { firstBaseUpdate: G, lastBaseUpdate: E } = H, U = H.shared.pending;
      if (U !== null) {
        H.shared.pending = null;
        var P = U, O = P.next;
        if (P.next = null, E === null)
          G = O;
        else
          E.next = O;
        E = P;
        var k = Z.alternate;
        if (k !== null) {
          var C = k.updateQueue, B = C.lastBaseUpdate;
          if (B !== E) {
            if (B === null)
              C.firstBaseUpdate = O;
            else
              B.next = O;
            C.lastBaseUpdate = P;
          }
        }
      }
      if (G !== null) {
        var v = H.baseState, h = n, f = null, q0 = null, k0 = null, w0 = G;
        do {
          var { lane: N1, eventTime: E1 } = w0;
          if (!EY(q, N1)) {
            var _ = {
              eventTime: E1,
              lane: N1,
              tag: w0.tag,
              payload: w0.payload,
              callback: w0.callback,
              next: null
            };
            if (k0 === null)
              q0 = k0 = _, f = v;
            else
              k0 = k0.next = _;
            h = Q1(h, N1);
          } else {
            if (k0 !== null) {
              var b = {
                eventTime: E1,
                lane: U8,
                tag: w0.tag,
                payload: w0.payload,
                callback: w0.callback,
                next: null
              };
              k0 = k0.next = b;
            }
            v = oI(Z, H, w0, v, X, $);
            var T = w0.callback;
            if (T !== null && w0.lane !== U8) {
              Z.flags |= I7;
              var a = H.effects;
              if (a === null)
                H.effects = [w0];
              else
                a.push(w0);
            }
          }
          if (w0 = w0.next, w0 === null)
            if (U = H.shared.pending, U === null)
              break;
            else {
              var E0 = U, H0 = E0.next;
              E0.next = null, w0 = H0, H.lastBaseUpdate = E0, H.shared.pending = null;
            }
        } while (!0);
        if (k0 === null)
          f = v;
        H.baseState = f, H.firstBaseUpdate = q0, H.lastBaseUpdate = k0;
        var g0 = H.shared.interleaved;
        if (g0 !== null) {
          var p0 = g0;
          do
            h = Q1(h, p0.lane), p0 = p0.next;
          while (p0 !== g0);
        } else if (G === null)
          H.shared.lanes = n;
        z3(h), Z.lanes = h, Z.memoizedState = v;
      }
      T9 = null;
    }
    function aI(Z, X) {
      if (typeof Z !== "function")
        throw new Error("Invalid argument passed as callback. Expected a function. Instead " + ("received: " + Z));
      Z.call(X);
    }
    function nA() {
      _9 = !1;
    }
    function v9() {
      return _9;
    }
    function sA(Z, X, $) {
      var q = X.effects;
      if (X.effects = null, q !== null)
        for (var H = 0;H < q.length; H++) {
          var G = q[H], E = G.callback;
          if (E !== null)
            G.callback = null, aI(E, $);
        }
    }
    var mW = {}, i4 = n4(mW), bW = n4(mW), h9 = n4(mW);
    function y9(Z) {
      if (Z === mW)
        throw new Error("Expected host context to exist. This error is likely caused by a bug in React. Please file an issue.");
      return Z;
    }
    function oA() {
      var Z = y9(h9.current);
      return Z;
    }
    function O2(Z, X) {
      r8(h9, X, Z), r8(bW, Z, Z), r8(i4, mW, Z);
      var $ = NS(X);
      a8(i4, Z), r8(i4, $, Z);
    }
    function _Y(Z) {
      a8(i4, Z), a8(bW, Z), a8(h9, Z);
    }
    function w2() {
      var Z = y9(i4.current);
      return Z;
    }
    function aA(Z) {
      var X = y9(h9.current), $ = y9(i4.current), q = ES($, Z.type);
      if ($ === q)
        return;
      r8(bW, Z, Z), r8(i4, q, Z);
    }
    function M2(Z) {
      if (bW.current !== Z)
        return;
      a8(i4, Z), a8(bW, Z);
    }
    var rI = 0, rA = 1, iA = 1, uW = 2, sZ = n4(rI);
    function D2(Z, X) {
      return (Z & X) !== 0;
    }
    function TY(Z) {
      return Z & rA;
    }
    function k2(Z, X) {
      return Z & rA | X;
    }
    function iI(Z, X) {
      return Z | X;
    }
    function t4(Z, X) {
      r8(sZ, X, Z);
    }
    function gY(Z) {
      a8(sZ, Z);
    }
    function tI(Z, X) {
      var $ = Z.memoizedState;
      if ($ !== null) {
        if ($.dehydrated !== null)
          return !0;
        return !1;
      }
      var q = Z.memoizedProps;
      return !0;
    }
    function f9(Z) {
      var X = Z;
      while (X !== null) {
        if (X.tag === l) {
          var $ = X.memoizedState;
          if ($ !== null) {
            var q = $.dehydrated;
            if (q === null || EA(q) || cG(q))
              return X;
          }
        } else if (X.tag === p && X.memoizedProps.revealOrder !== void 0) {
          var H = (X.flags & I1) !== S0;
          if (H)
            return X;
        } else if (X.child !== null) {
          X.child.return = X, X = X.child;
          continue;
        }
        if (X === Z)
          return null;
        while (X.sibling === null) {
          if (X.return === null || X.return === Z)
            return null;
          X = X.return;
        }
        X.sibling.return = X.return, X = X.sibling;
      }
      return null;
    }
    var TQ = 0, o6 = 1, VX = 2, a6 = 4, I8 = 8, R2 = [];
    function j2() {
      for (var Z = 0;Z < R2.length; Z++) {
        var X = R2[Z];
        X._workInProgressVersionPrimary = null;
      }
      R2.length = 0;
    }
    function eI(Z, X) {
      var $ = X._getVersion, q = $(X._source);
      if (Z.mutableSourceEagerHydrationData == null)
        Z.mutableSourceEagerHydrationData = [X, q];
      else
        Z.mutableSourceEagerHydrationData.push(X, q);
    }
    var { ReactCurrentDispatcher: z0, ReactCurrentBatchConfig: cW } = Q, B2, xY;
    B2 = /* @__PURE__ */ new Set;
    var F$ = n, u1 = null, r6 = null, i6 = null, m9 = !1, pW = !1, dW = 0, Q_ = 0, Z_ = 25, c = null, EZ = null, e4 = -1, C2 = !1;
    function T1() {
      {
        var Z = c;
        if (EZ === null)
          EZ = [Z];
        else
          EZ.push(Z);
      }
    }
    function X0() {
      {
        var Z = c;
        if (EZ !== null) {
          if (e4++, EZ[e4] !== Z)
            X_(Z);
        }
      }
    }
    function vY(Z) {
      if (Z !== void 0 && Z !== null && !S1(Z))
        K("%s received a final argument that is not an array (instead, received `%s`). When specified, the final argument must be an array.", c, typeof Z);
    }
    function X_(Z) {
      {
        var X = V0(u1);
        if (!B2.has(X)) {
          if (B2.add(X), EZ !== null) {
            var $ = "", q = 30;
            for (var H = 0;H <= e4; H++) {
              var G = EZ[H], E = H === e4 ? Z : G, U = H + 1 + ". " + G;
              while (U.length < q)
                U += " ";
              U += E + `
`, $ += U;
            }
            K(`React has detected a change in the order of Hooks called by %s. This will lead to bugs and errors if not fixed. For more information, read the Rules of Hooks: https://reactjs.org/link/rules-of-hooks

   Previous render            Next render
   ------------------------------------------------------
%s   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
`, X, $);
          }
        }
      }
    }
    function i8() {
      throw new Error(`Invalid hook call. Hooks can only be called inside of the body of a function component. This could happen for one of the following reasons:
1. You might have mismatching versions of React and the renderer (such as React DOM)
2. You might be breaking the Rules of Hooks
3. You might have more than one copy of React in the same app
See https://reactjs.org/link/invalid-hook-call for tips about how to debug and fix this problem.`);
    }
    function V2(Z, X) {
      if (C2)
        return !1;
      if (X === null)
        return K("%s received a final argument during this render, but not during the previous render. Even though the final argument is optional, its type cannot change between renders.", c), !1;
      if (Z.length !== X.length)
        K(`The final argument passed to %s changed size between renders. The order and size of this array must remain constant.

Previous: %s
Incoming: %s`, c, "[" + X.join(", ") + "]", "[" + Z.join(", ") + "]");
      for (var $ = 0;$ < X.length && $ < Z.length; $++) {
        if (aQ(Z[$], X[$]))
          continue;
        return !1;
      }
      return !0;
    }
    function hY(Z, X, $, q, H, G) {
      if (F$ = G, u1 = X, EZ = Z !== null ? Z._debugHookTypes : null, e4 = -1, C2 = Z !== null && Z.type !== X.type, X.memoizedState = null, X.updateQueue = null, X.lanes = n, Z !== null && Z.memoizedState !== null)
        z0.current = OL;
      else if (EZ !== null)
        z0.current = LL;
      else
        z0.current = AL;
      var E = $(q, H);
      if (pW) {
        var U = 0;
        do {
          if (pW = !1, dW = 0, U >= Z_)
            throw new Error("Too many re-renders. React limits the number of renders to prevent an infinite loop.");
          U += 1, C2 = !1, r6 = null, i6 = null, X.updateQueue = null, e4 = -1, z0.current = wL, E = $(q, H);
        } while (pW);
      }
      z0.current = Q5, X._debugHookTypes = EZ;
      var P = r6 !== null && r6.next !== null;
      if (F$ = n, u1 = null, r6 = null, i6 = null, c = null, EZ = null, e4 = -1, Z !== null && (Z.flags & X4) !== (X.flags & X4) && (Z.mode & A1) !== B0)
        K("Internal React error: Expected static flag was missing. Please notify the React team.");
      if (m9 = !1, P)
        throw new Error("Rendered fewer hooks than expected. This may be caused by an accidental early return statement.");
      return E;
    }
    function yY() {
      var Z = dW !== 0;
      return dW = 0, Z;
    }
    function tA(Z, X, $) {
      if (X.updateQueue = Z.updateQueue, (X.mode & RX) !== B0)
        X.flags &= ~(TK | Z4 | uZ | O1);
      else
        X.flags &= ~(uZ | O1);
      Z.lanes = mK(Z.lanes, $);
    }
    function eA() {
      if (z0.current = Q5, m9) {
        var Z = u1.memoizedState;
        while (Z !== null) {
          var X = Z.queue;
          if (X !== null)
            X.pending = null;
          Z = Z.next;
        }
        m9 = !1;
      }
      F$ = n, u1 = null, r6 = null, i6 = null, EZ = null, e4 = -1, c = null, NL = !1, pW = !1, dW = 0;
    }
    function SX() {
      var Z = {
        memoizedState: null,
        baseState: null,
        baseQueue: null,
        queue: null,
        next: null
      };
      if (i6 === null)
        u1.memoizedState = i6 = Z;
      else
        i6 = i6.next = Z;
      return i6;
    }
    function FZ() {
      var Z;
      if (r6 === null) {
        var X = u1.alternate;
        if (X !== null)
          Z = X.memoizedState;
        else
          Z = null;
      } else
        Z = r6.next;
      var $;
      if (i6 === null)
        $ = u1.memoizedState;
      else
        $ = i6.next;
      if ($ !== null)
        i6 = $, $ = i6.next, r6 = Z;
      else {
        if (Z === null)
          throw new Error("Rendered more hooks than during the previous render.");
        r6 = Z;
        var q = {
          memoizedState: r6.memoizedState,
          baseState: r6.baseState,
          baseQueue: r6.baseQueue,
          queue: r6.queue,
          next: null
        };
        if (i6 === null)
          u1.memoizedState = i6 = q;
        else
          i6 = i6.next = q;
      }
      return i6;
    }
    function QL() {
      return {
        lastEffect: null,
        stores: null
      };
    }
    function S2(Z, X) {
      return typeof X === "function" ? X(Z) : X;
    }
    function I2(Z, X, $) {
      var q = SX(), H;
      if ($ !== void 0)
        H = $(X);
      else
        H = X;
      q.memoizedState = q.baseState = H;
      var G = {
        pending: null,
        interleaved: null,
        lanes: n,
        dispatch: null,
        lastRenderedReducer: Z,
        lastRenderedState: H
      };
      q.queue = G;
      var E = G.dispatch = Y_.bind(null, u1, G);
      return [q.memoizedState, E];
    }
    function _2(Z, X, $) {
      var q = FZ(), H = q.queue;
      if (H === null)
        throw new Error("Should have a queue. This is likely a bug in React. Please file an issue.");
      H.lastRenderedReducer = Z;
      var G = r6, E = G.baseQueue, U = H.pending;
      if (U !== null) {
        if (E !== null) {
          var P = E.next, O = U.next;
          E.next = O, U.next = P;
        }
        if (G.baseQueue !== E)
          K("Internal error: Expected work-in-progress queue to be a clone. This is a bug in React.");
        G.baseQueue = E = U, H.pending = null;
      }
      if (E !== null) {
        var k = E.next, C = G.baseState, B = null, v = null, h = null, f = k;
        do {
          var q0 = f.lane;
          if (!EY(F$, q0)) {
            var k0 = {
              lane: q0,
              action: f.action,
              hasEagerState: f.hasEagerState,
              eagerState: f.eagerState,
              next: null
            };
            if (h === null)
              v = h = k0, B = C;
            else
              h = h.next = k0;
            u1.lanes = Q1(u1.lanes, q0), z3(q0);
          } else {
            if (h !== null) {
              var w0 = {
                lane: U8,
                action: f.action,
                hasEagerState: f.hasEagerState,
                eagerState: f.eagerState,
                next: null
              };
              h = h.next = w0;
            }
            if (f.hasEagerState)
              C = f.eagerState;
            else {
              var N1 = f.action;
              C = Z(C, N1);
            }
          }
          f = f.next;
        } while (f !== null && f !== k);
        if (h === null)
          B = C;
        else
          h.next = v;
        if (!aQ(C, q.memoizedState))
          eW();
        q.memoizedState = C, q.baseState = B, q.baseQueue = h, H.lastRenderedState = C;
      }
      var E1 = H.interleaved;
      if (E1 !== null) {
        var _ = E1;
        do {
          var b = _.lane;
          u1.lanes = Q1(u1.lanes, b), z3(b), _ = _.next;
        } while (_ !== E1);
      } else if (E === null)
        H.lanes = n;
      var T = H.dispatch;
      return [q.memoizedState, T];
    }
    function T2(Z, X, $) {
      var q = FZ(), H = q.queue;
      if (H === null)
        throw new Error("Should have a queue. This is likely a bug in React. Please file an issue.");
      H.lastRenderedReducer = Z;
      var { dispatch: G, pending: E } = H, U = q.memoizedState;
      if (E !== null) {
        H.pending = null;
        var P = E.next, O = P;
        do {
          var k = O.action;
          U = Z(U, k), O = O.next;
        } while (O !== P);
        if (!aQ(U, q.memoizedState))
          eW();
        if (q.memoizedState = U, q.baseQueue === null)
          q.baseState = U;
        H.lastRenderedState = U;
      }
      return [U, G];
    }
    function g2(Z, X, $) {
      return;
    }
    function b9(Z, X, $) {
      return;
    }
    function x2(Z, X, $) {
      var q = u1, H = SX(), G, E = S8();
      if (E) {
        if ($ === void 0)
          throw new Error("Missing getServerSnapshot, which is required for server-rendered content. Will revert to client rendering.");
        if (G = $(), !xY) {
          if (G !== $())
            K("The result of getServerSnapshot should be cached to avoid an infinite loop"), xY = !0;
        }
      } else {
        if (G = X(), !xY) {
          var U = X();
          if (!aQ(G, U))
            K("The result of getSnapshot should be cached to avoid an infinite loop"), xY = !0;
        }
        var P = O5();
        if (P === null)
          throw new Error("Expected a work-in-progress root. This is a bug in React. Please file an issue.");
        if (!fK(P, F$))
          ZL(q, X, G);
      }
      H.memoizedState = G;
      var O = {
        value: G,
        getSnapshot: X
      };
      return H.queue = O, l9(JL.bind(null, q, O, Z), [Z]), q.flags |= uZ, lW(o6 | I8, XL.bind(null, q, O, G, X), void 0, null), G;
    }
    function u9(Z, X, $) {
      var q = u1, H = FZ(), G = X();
      if (!xY) {
        var E = X();
        if (!aQ(G, E))
          K("The result of getSnapshot should be cached to avoid an infinite loop"), xY = !0;
      }
      var U = H.memoizedState, P = !aQ(U, G);
      if (P)
        H.memoizedState = G, eW();
      var O = H.queue;
      if (sW(JL.bind(null, q, O, Z), [Z]), O.getSnapshot !== X || P || i6 !== null && i6.memoizedState.tag & o6) {
        q.flags |= uZ, lW(o6 | I8, XL.bind(null, q, O, G, X), void 0, null);
        var k = O5();
        if (k === null)
          throw new Error("Expected a work-in-progress root. This is a bug in React. Please file an issue.");
        if (!fK(k, F$))
          ZL(q, X, G);
      }
      return G;
    }
    function ZL(Z, X, $) {
      Z.flags |= _K;
      var q = {
        getSnapshot: X,
        value: $
      }, H = u1.updateQueue;
      if (H === null)
        H = QL(), u1.updateQueue = H, H.stores = [q];
      else {
        var G = H.stores;
        if (G === null)
          H.stores = [q];
        else
          G.push(q);
      }
    }
    function XL(Z, X, $, q) {
      if (X.value = $, X.getSnapshot = q, $L(X))
        YL(Z);
    }
    function JL(Z, X, $) {
      var q = function() {
        if ($L(X))
          YL(Z);
      };
      return $(q);
    }
    function $L(Z) {
      var { getSnapshot: X, value: $ } = Z;
      try {
        var q = X();
        return !aQ($, q);
      } catch (H) {
        return !0;
      }
    }
    function YL(Z) {
      var X = _Q(Z, b0);
      if (X !== null)
        Z8(X, Z, b0, J6);
    }
    function c9(Z) {
      var X = SX();
      if (typeof Z === "function")
        Z = Z();
      X.memoizedState = X.baseState = Z;
      var $ = {
        pending: null,
        interleaved: null,
        lanes: n,
        dispatch: null,
        lastRenderedReducer: S2,
        lastRenderedState: Z
      };
      X.queue = $;
      var q = $.dispatch = q_.bind(null, u1, $);
      return [X.memoizedState, q];
    }
    function v2(Z) {
      return _2(S2);
    }
    function h2(Z) {
      return T2(S2);
    }
    function lW(Z, X, $, q) {
      var H = {
        tag: Z,
        create: X,
        destroy: $,
        deps: q,
        next: null
      }, G = u1.updateQueue;
      if (G === null)
        G = QL(), u1.updateQueue = G, G.lastEffect = H.next = H;
      else {
        var E = G.lastEffect;
        if (E === null)
          G.lastEffect = H.next = H;
        else {
          var U = E.next;
          E.next = H, H.next = U, G.lastEffect = H;
        }
      }
      return H;
    }
    function y2(Z) {
      var X = SX();
      {
        var $ = {
          current: Z
        };
        return X.memoizedState = $, $;
      }
    }
    function p9(Z) {
      var X = FZ();
      return X.memoizedState;
    }
    function nW(Z, X, $, q) {
      var H = SX(), G = q === void 0 ? null : q;
      u1.flags |= Z, H.memoizedState = lW(o6 | X, $, void 0, G);
    }
    function d9(Z, X, $, q) {
      var H = FZ(), G = q === void 0 ? null : q, E = void 0;
      if (r6 !== null) {
        var U = r6.memoizedState;
        if (E = U.destroy, G !== null) {
          var P = U.deps;
          if (V2(G, P)) {
            H.memoizedState = lW(X, $, E, G);
            return;
          }
        }
      }
      u1.flags |= Z, H.memoizedState = lW(o6 | X, $, E, G);
    }
    function l9(Z, X) {
      if ((u1.mode & RX) !== B0)
        return nW(TK | uZ | g7, I8, Z, X);
      else
        return nW(uZ | g7, I8, Z, X);
    }
    function sW(Z, X) {
      return d9(uZ, I8, Z, X);
    }
    function f2(Z, X) {
      return nW(O1, VX, Z, X);
    }
    function n9(Z, X) {
      return d9(O1, VX, Z, X);
    }
    function m2(Z, X) {
      var $ = O1;
      if ($ |= rJ, (u1.mode & RX) !== B0)
        $ |= Z4;
      return nW($, a6, Z, X);
    }
    function s9(Z, X) {
      return d9(O1, a6, Z, X);
    }
    function qL(Z, X) {
      if (typeof X === "function") {
        var $ = X, q = Z();
        return $(q), function() {
          $(null);
        };
      } else if (X !== null && X !== void 0) {
        var H = X;
        if (!H.hasOwnProperty("current"))
          K("Expected useImperativeHandle() first argument to either be a ref callback or React.createRef() object. Instead received: %s.", "an object with keys {" + Object.keys(H).join(", ") + "}");
        var G = Z();
        return H.current = G, function() {
          H.current = null;
        };
      }
    }
    function b2(Z, X, $) {
      if (typeof X !== "function")
        K("Expected useImperativeHandle() second argument to be a function that creates a handle. Instead received: %s.", X !== null ? typeof X : "null");
      var q = $ !== null && $ !== void 0 ? $.concat([Z]) : null, H = O1;
      if (H |= rJ, (u1.mode & RX) !== B0)
        H |= Z4;
      return nW(H, a6, qL.bind(null, X, Z), q);
    }
    function o9(Z, X, $) {
      if (typeof X !== "function")
        K("Expected useImperativeHandle() second argument to be a function that creates a handle. Instead received: %s.", X !== null ? typeof X : "null");
      var q = $ !== null && $ !== void 0 ? $.concat([Z]) : null;
      return d9(O1, a6, qL.bind(null, X, Z), q);
    }
    function a9(Z, X) {}
    var r9 = a9;
    function u2(Z, X) {
      var $ = SX(), q = X === void 0 ? null : X;
      return $.memoizedState = [Z, q], Z;
    }
    function i9(Z, X) {
      var $ = FZ(), q = X === void 0 ? null : X, H = $.memoizedState;
      if (H !== null) {
        if (q !== null) {
          var G = H[1];
          if (V2(q, G))
            return H[0];
        }
      }
      return $.memoizedState = [Z, q], Z;
    }
    function c2(Z, X) {
      var $ = SX(), q = X === void 0 ? null : X, H = Z();
      return $.memoizedState = [H, q], H;
    }
    function t9(Z, X) {
      var $ = FZ(), q = X === void 0 ? null : X, H = $.memoizedState;
      if (H !== null) {
        if (q !== null) {
          var G = H[1];
          if (V2(q, G))
            return H[0];
        }
      }
      var E = Z();
      return $.memoizedState = [E, q], E;
    }
    function p2(Z) {
      var X = SX();
      return X.memoizedState = Z, Z;
    }
    function WL(Z) {
      var X = FZ(), $ = r6, q = $.memoizedState;
      return HL(X, q, Z);
    }
    function KL(Z) {
      var X = FZ();
      if (r6 === null)
        return X.memoizedState = Z, Z;
      else {
        var $ = r6.memoizedState;
        return HL(X, $, Z);
      }
    }
    function HL(Z, X, $) {
      var q = !cB(F$);
      if (q) {
        if (!aQ($, X)) {
          var H = $P();
          u1.lanes = Q1(u1.lanes, H), z3(H), Z.baseState = !0;
        }
        return X;
      } else {
        if (Z.baseState)
          Z.baseState = !1, eW();
        return Z.memoizedState = $, $;
      }
    }
    function J_(Z, X, $) {
      var q = pZ();
      P8(iB(q, $4)), Z(!0);
      var H = cW.transition;
      cW.transition = {};
      var G = cW.transition;
      cW.transition._updatedFibers = /* @__PURE__ */ new Set;
      try {
        Z(!1), X();
      } finally {
        if (P8(q), cW.transition = H, H === null && G._updatedFibers) {
          var E = G._updatedFibers.size;
          if (E > 10)
            W("Detected a large number of updates inside startTransition. If this is due to a subscription please re-write it to use React provided hooks. Otherwise concurrent mode guarantees are off the table.");
          G._updatedFibers.clear();
        }
      }
    }
    function d2() {
      var Z = c9(!1), X = Z[0], $ = Z[1], q = J_.bind(null, $), H = SX();
      return H.memoizedState = q, [X, q];
    }
    function GL() {
      var Z = v2(), X = Z[0], $ = FZ(), q = $.memoizedState;
      return [X, q];
    }
    function zL() {
      var Z = h2(), X = Z[0], $ = FZ(), q = $.memoizedState;
      return [X, q];
    }
    var NL = !1;
    function $_() {
      return NL;
    }
    function l2() {
      var Z = SX(), X = O5(), $ = X.identifierPrefix, q;
      if (S8()) {
        var H = DI();
        q = ":" + $ + "R" + H;
        var G = dW++;
        if (G > 0)
          q += "H" + G.toString(32);
        q += ":";
      } else {
        var E = Q_++;
        q = ":" + $ + "r" + E.toString(32) + ":";
      }
      return Z.memoizedState = q, q;
    }
    function e9() {
      var Z = FZ(), X = Z.memoizedState;
      return X;
    }
    function Y_(Z, X, $) {
      if (typeof arguments[3] === "function")
        K("State updates from the useState() and useReducer() Hooks don't support the second callback argument. To execute a side effect after rendering, declare it in the component body with useEffect().");
      var q = $J(Z), H = {
        lane: q,
        action: $,
        hasEagerState: !1,
        eagerState: null,
        next: null
      };
      if (EL(Z))
        FL(X, H);
      else {
        var G = cA(Z, X, H, q);
        if (G !== null) {
          var E = UQ();
          Z8(G, Z, q, E), UL(G, X, q);
        }
      }
      PL(Z, q);
    }
    function q_(Z, X, $) {
      if (typeof arguments[3] === "function")
        K("State updates from the useState() and useReducer() Hooks don't support the second callback argument. To execute a side effect after rendering, declare it in the component body with useEffect().");
      var q = $J(Z), H = {
        lane: q,
        action: $,
        hasEagerState: !1,
        eagerState: null,
        next: null
      };
      if (EL(Z))
        FL(X, H);
      else {
        var G = Z.alternate;
        if (Z.lanes === n && (G === null || G.lanes === n)) {
          var E = X.lastRenderedReducer;
          if (E !== null) {
            var U;
            U = z0.current, z0.current = oZ;
            try {
              var P = X.lastRenderedState, O = E(P, $);
              if (H.hasEagerState = !0, H.eagerState = O, aQ(O, P)) {
                lI(Z, X, H, q);
                return;
              }
            } catch (B) {} finally {
              z0.current = U;
            }
          }
        }
        var k = cA(Z, X, H, q);
        if (k !== null) {
          var C = UQ();
          Z8(k, Z, q, C), UL(k, X, q);
        }
      }
      PL(Z, q);
    }
    function EL(Z) {
      var X = Z.alternate;
      return Z === u1 || X !== null && X === u1;
    }
    function FL(Z, X) {
      pW = m9 = !0;
      var $ = Z.pending;
      if ($ === null)
        X.next = X;
      else
        X.next = $.next, $.next = X;
      Z.pending = X;
    }
    function UL(Z, X, $) {
      if (JP($)) {
        var q = X.lanes;
        q = YP(q, Z.pendingLanes);
        var H = Q1(q, $);
        X.lanes = H, HG(Z, H);
      }
    }
    function PL(Z, X, $) {
      f7(Z, X);
    }
    var Q5 = {
      readContext: b6,
      useCallback: i8,
      useContext: i8,
      useEffect: i8,
      useImperativeHandle: i8,
      useInsertionEffect: i8,
      useLayoutEffect: i8,
      useMemo: i8,
      useReducer: i8,
      useRef: i8,
      useState: i8,
      useDebugValue: i8,
      useDeferredValue: i8,
      useTransition: i8,
      useMutableSource: i8,
      useSyncExternalStore: i8,
      useId: i8,
      unstable_isNewReconciler: W0
    }, AL = null, LL = null, OL = null, wL = null, IX = null, oZ = null, Z5 = null;
    {
      var n2 = function() {
        K("Context can only be read while React is rendering. In classes, you can read it in the render method or getDerivedStateFromProps. In function components, you can read it directly in the function body, but not inside Hooks like useReducer() or useMemo().");
      }, u0 = function() {
        K("Do not call Hooks inside useEffect(...), useMemo(...), or other built-in Hooks. You can only call Hooks at the top level of your React function. For more information, see https://reactjs.org/link/rules-of-hooks");
      };
      AL = {
        readContext: function(Z) {
          return b6(Z);
        },
        useCallback: function(Z, X) {
          return c = "useCallback", T1(), vY(X), u2(Z, X);
        },
        useContext: function(Z) {
          return c = "useContext", T1(), b6(Z);
        },
        useEffect: function(Z, X) {
          return c = "useEffect", T1(), vY(X), l9(Z, X);
        },
        useImperativeHandle: function(Z, X, $) {
          return c = "useImperativeHandle", T1(), vY($), b2(Z, X, $);
        },
        useInsertionEffect: function(Z, X) {
          return c = "useInsertionEffect", T1(), vY(X), f2(Z, X);
        },
        useLayoutEffect: function(Z, X) {
          return c = "useLayoutEffect", T1(), vY(X), m2(Z, X);
        },
        useMemo: function(Z, X) {
          c = "useMemo", T1(), vY(X);
          var $ = z0.current;
          z0.current = IX;
          try {
            return c2(Z, X);
          } finally {
            z0.current = $;
          }
        },
        useReducer: function(Z, X, $) {
          c = "useReducer", T1();
          var q = z0.current;
          z0.current = IX;
          try {
            return I2(Z, X, $);
          } finally {
            z0.current = q;
          }
        },
        useRef: function(Z) {
          return c = "useRef", T1(), y2(Z);
        },
        useState: function(Z) {
          c = "useState", T1();
          var X = z0.current;
          z0.current = IX;
          try {
            return c9(Z);
          } finally {
            z0.current = X;
          }
        },
        useDebugValue: function(Z, X) {
          return c = "useDebugValue", T1(), a9();
        },
        useDeferredValue: function(Z) {
          return c = "useDeferredValue", T1(), p2(Z);
        },
        useTransition: function() {
          return c = "useTransition", T1(), d2();
        },
        useMutableSource: function(Z, X, $) {
          return c = "useMutableSource", T1(), g2();
        },
        useSyncExternalStore: function(Z, X, $) {
          return c = "useSyncExternalStore", T1(), x2(Z, X, $);
        },
        useId: function() {
          return c = "useId", T1(), l2();
        },
        unstable_isNewReconciler: W0
      }, LL = {
        readContext: function(Z) {
          return b6(Z);
        },
        useCallback: function(Z, X) {
          return c = "useCallback", X0(), u2(Z, X);
        },
        useContext: function(Z) {
          return c = "useContext", X0(), b6(Z);
        },
        useEffect: function(Z, X) {
          return c = "useEffect", X0(), l9(Z, X);
        },
        useImperativeHandle: function(Z, X, $) {
          return c = "useImperativeHandle", X0(), b2(Z, X, $);
        },
        useInsertionEffect: function(Z, X) {
          return c = "useInsertionEffect", X0(), f2(Z, X);
        },
        useLayoutEffect: function(Z, X) {
          return c = "useLayoutEffect", X0(), m2(Z, X);
        },
        useMemo: function(Z, X) {
          c = "useMemo", X0();
          var $ = z0.current;
          z0.current = IX;
          try {
            return c2(Z, X);
          } finally {
            z0.current = $;
          }
        },
        useReducer: function(Z, X, $) {
          c = "useReducer", X0();
          var q = z0.current;
          z0.current = IX;
          try {
            return I2(Z, X, $);
          } finally {
            z0.current = q;
          }
        },
        useRef: function(Z) {
          return c = "useRef", X0(), y2(Z);
        },
        useState: function(Z) {
          c = "useState", X0();
          var X = z0.current;
          z0.current = IX;
          try {
            return c9(Z);
          } finally {
            z0.current = X;
          }
        },
        useDebugValue: function(Z, X) {
          return c = "useDebugValue", X0(), a9();
        },
        useDeferredValue: function(Z) {
          return c = "useDeferredValue", X0(), p2(Z);
        },
        useTransition: function() {
          return c = "useTransition", X0(), d2();
        },
        useMutableSource: function(Z, X, $) {
          return c = "useMutableSource", X0(), g2();
        },
        useSyncExternalStore: function(Z, X, $) {
          return c = "useSyncExternalStore", X0(), x2(Z, X, $);
        },
        useId: function() {
          return c = "useId", X0(), l2();
        },
        unstable_isNewReconciler: W0
      }, OL = {
        readContext: function(Z) {
          return b6(Z);
        },
        useCallback: function(Z, X) {
          return c = "useCallback", X0(), i9(Z, X);
        },
        useContext: function(Z) {
          return c = "useContext", X0(), b6(Z);
        },
        useEffect: function(Z, X) {
          return c = "useEffect", X0(), sW(Z, X);
        },
        useImperativeHandle: function(Z, X, $) {
          return c = "useImperativeHandle", X0(), o9(Z, X, $);
        },
        useInsertionEffect: function(Z, X) {
          return c = "useInsertionEffect", X0(), n9(Z, X);
        },
        useLayoutEffect: function(Z, X) {
          return c = "useLayoutEffect", X0(), s9(Z, X);
        },
        useMemo: function(Z, X) {
          c = "useMemo", X0();
          var $ = z0.current;
          z0.current = oZ;
          try {
            return t9(Z, X);
          } finally {
            z0.current = $;
          }
        },
        useReducer: function(Z, X, $) {
          c = "useReducer", X0();
          var q = z0.current;
          z0.current = oZ;
          try {
            return _2(Z, X, $);
          } finally {
            z0.current = q;
          }
        },
        useRef: function(Z) {
          return c = "useRef", X0(), p9();
        },
        useState: function(Z) {
          c = "useState", X0();
          var X = z0.current;
          z0.current = oZ;
          try {
            return v2(Z);
          } finally {
            z0.current = X;
          }
        },
        useDebugValue: function(Z, X) {
          return c = "useDebugValue", X0(), r9();
        },
        useDeferredValue: function(Z) {
          return c = "useDeferredValue", X0(), WL(Z);
        },
        useTransition: function() {
          return c = "useTransition", X0(), GL();
        },
        useMutableSource: function(Z, X, $) {
          return c = "useMutableSource", X0(), b9();
        },
        useSyncExternalStore: function(Z, X, $) {
          return c = "useSyncExternalStore", X0(), u9(Z, X);
        },
        useId: function() {
          return c = "useId", X0(), e9();
        },
        unstable_isNewReconciler: W0
      }, wL = {
        readContext: function(Z) {
          return b6(Z);
        },
        useCallback: function(Z, X) {
          return c = "useCallback", X0(), i9(Z, X);
        },
        useContext: function(Z) {
          return c = "useContext", X0(), b6(Z);
        },
        useEffect: function(Z, X) {
          return c = "useEffect", X0(), sW(Z, X);
        },
        useImperativeHandle: function(Z, X, $) {
          return c = "useImperativeHandle", X0(), o9(Z, X, $);
        },
        useInsertionEffect: function(Z, X) {
          return c = "useInsertionEffect", X0(), n9(Z, X);
        },
        useLayoutEffect: function(Z, X) {
          return c = "useLayoutEffect", X0(), s9(Z, X);
        },
        useMemo: function(Z, X) {
          c = "useMemo", X0();
          var $ = z0.current;
          z0.current = Z5;
          try {
            return t9(Z, X);
          } finally {
            z0.current = $;
          }
        },
        useReducer: function(Z, X, $) {
          c = "useReducer", X0();
          var q = z0.current;
          z0.current = Z5;
          try {
            return T2(Z, X, $);
          } finally {
            z0.current = q;
          }
        },
        useRef: function(Z) {
          return c = "useRef", X0(), p9();
        },
        useState: function(Z) {
          c = "useState", X0();
          var X = z0.current;
          z0.current = Z5;
          try {
            return h2(Z);
          } finally {
            z0.current = X;
          }
        },
        useDebugValue: function(Z, X) {
          return c = "useDebugValue", X0(), r9();
        },
        useDeferredValue: function(Z) {
          return c = "useDeferredValue", X0(), KL(Z);
        },
        useTransition: function() {
          return c = "useTransition", X0(), zL();
        },
        useMutableSource: function(Z, X, $) {
          return c = "useMutableSource", X0(), b9();
        },
        useSyncExternalStore: function(Z, X, $) {
          return c = "useSyncExternalStore", X0(), u9(Z, X);
        },
        useId: function() {
          return c = "useId", X0(), e9();
        },
        unstable_isNewReconciler: W0
      }, IX = {
        readContext: function(Z) {
          return n2(), b6(Z);
        },
        useCallback: function(Z, X) {
          return c = "useCallback", u0(), T1(), u2(Z, X);
        },
        useContext: function(Z) {
          return c = "useContext", u0(), T1(), b6(Z);
        },
        useEffect: function(Z, X) {
          return c = "useEffect", u0(), T1(), l9(Z, X);
        },
        useImperativeHandle: function(Z, X, $) {
          return c = "useImperativeHandle", u0(), T1(), b2(Z, X, $);
        },
        useInsertionEffect: function(Z, X) {
          return c = "useInsertionEffect", u0(), T1(), f2(Z, X);
        },
        useLayoutEffect: function(Z, X) {
          return c = "useLayoutEffect", u0(), T1(), m2(Z, X);
        },
        useMemo: function(Z, X) {
          c = "useMemo", u0(), T1();
          var $ = z0.current;
          z0.current = IX;
          try {
            return c2(Z, X);
          } finally {
            z0.current = $;
          }
        },
        useReducer: function(Z, X, $) {
          c = "useReducer", u0(), T1();
          var q = z0.current;
          z0.current = IX;
          try {
            return I2(Z, X, $);
          } finally {
            z0.current = q;
          }
        },
        useRef: function(Z) {
          return c = "useRef", u0(), T1(), y2(Z);
        },
        useState: function(Z) {
          c = "useState", u0(), T1();
          var X = z0.current;
          z0.current = IX;
          try {
            return c9(Z);
          } finally {
            z0.current = X;
          }
        },
        useDebugValue: function(Z, X) {
          return c = "useDebugValue", u0(), T1(), a9();
        },
        useDeferredValue: function(Z) {
          return c = "useDeferredValue", u0(), T1(), p2(Z);
        },
        useTransition: function() {
          return c = "useTransition", u0(), T1(), d2();
        },
        useMutableSource: function(Z, X, $) {
          return c = "useMutableSource", u0(), T1(), g2();
        },
        useSyncExternalStore: function(Z, X, $) {
          return c = "useSyncExternalStore", u0(), T1(), x2(Z, X, $);
        },
        useId: function() {
          return c = "useId", u0(), T1(), l2();
        },
        unstable_isNewReconciler: W0
      }, oZ = {
        readContext: function(Z) {
          return n2(), b6(Z);
        },
        useCallback: function(Z, X) {
          return c = "useCallback", u0(), X0(), i9(Z, X);
        },
        useContext: function(Z) {
          return c = "useContext", u0(), X0(), b6(Z);
        },
        useEffect: function(Z, X) {
          return c = "useEffect", u0(), X0(), sW(Z, X);
        },
        useImperativeHandle: function(Z, X, $) {
          return c = "useImperativeHandle", u0(), X0(), o9(Z, X, $);
        },
        useInsertionEffect: function(Z, X) {
          return c = "useInsertionEffect", u0(), X0(), n9(Z, X);
        },
        useLayoutEffect: function(Z, X) {
          return c = "useLayoutEffect", u0(), X0(), s9(Z, X);
        },
        useMemo: function(Z, X) {
          c = "useMemo", u0(), X0();
          var $ = z0.current;
          z0.current = oZ;
          try {
            return t9(Z, X);
          } finally {
            z0.current = $;
          }
        },
        useReducer: function(Z, X, $) {
          c = "useReducer", u0(), X0();
          var q = z0.current;
          z0.current = oZ;
          try {
            return _2(Z, X, $);
          } finally {
            z0.current = q;
          }
        },
        useRef: function(Z) {
          return c = "useRef", u0(), X0(), p9();
        },
        useState: function(Z) {
          c = "useState", u0(), X0();
          var X = z0.current;
          z0.current = oZ;
          try {
            return v2(Z);
          } finally {
            z0.current = X;
          }
        },
        useDebugValue: function(Z, X) {
          return c = "useDebugValue", u0(), X0(), r9();
        },
        useDeferredValue: function(Z) {
          return c = "useDeferredValue", u0(), X0(), WL(Z);
        },
        useTransition: function() {
          return c = "useTransition", u0(), X0(), GL();
        },
        useMutableSource: function(Z, X, $) {
          return c = "useMutableSource", u0(), X0(), b9();
        },
        useSyncExternalStore: function(Z, X, $) {
          return c = "useSyncExternalStore", u0(), X0(), u9(Z, X);
        },
        useId: function() {
          return c = "useId", u0(), X0(), e9();
        },
        unstable_isNewReconciler: W0
      }, Z5 = {
        readContext: function(Z) {
          return n2(), b6(Z);
        },
        useCallback: function(Z, X) {
          return c = "useCallback", u0(), X0(), i9(Z, X);
        },
        useContext: function(Z) {
          return c = "useContext", u0(), X0(), b6(Z);
        },
        useEffect: function(Z, X) {
          return c = "useEffect", u0(), X0(), sW(Z, X);
        },
        useImperativeHandle: function(Z, X, $) {
          return c = "useImperativeHandle", u0(), X0(), o9(Z, X, $);
        },
        useInsertionEffect: function(Z, X) {
          return c = "useInsertionEffect", u0(), X0(), n9(Z, X);
        },
        useLayoutEffect: function(Z, X) {
          return c = "useLayoutEffect", u0(), X0(), s9(Z, X);
        },
        useMemo: function(Z, X) {
          c = "useMemo", u0(), X0();
          var $ = z0.current;
          z0.current = oZ;
          try {
            return t9(Z, X);
          } finally {
            z0.current = $;
          }
        },
        useReducer: function(Z, X, $) {
          c = "useReducer", u0(), X0();
          var q = z0.current;
          z0.current = oZ;
          try {
            return T2(Z, X, $);
          } finally {
            z0.current = q;
          }
        },
        useRef: function(Z) {
          return c = "useRef", u0(), X0(), p9();
        },
        useState: function(Z) {
          c = "useState", u0(), X0();
          var X = z0.current;
          z0.current = oZ;
          try {
            return h2(Z);
          } finally {
            z0.current = X;
          }
        },
        useDebugValue: function(Z, X) {
          return c = "useDebugValue", u0(), X0(), r9();
        },
        useDeferredValue: function(Z) {
          return c = "useDeferredValue", u0(), X0(), KL(Z);
        },
        useTransition: function() {
          return c = "useTransition", u0(), X0(), zL();
        },
        useMutableSource: function(Z, X, $) {
          return c = "useMutableSource", u0(), X0(), b9();
        },
        useSyncExternalStore: function(Z, X, $) {
          return c = "useSyncExternalStore", u0(), X0(), u9(Z, X);
        },
        useId: function() {
          return c = "useId", u0(), X0(), e9();
        },
        unstable_isNewReconciler: W0
      };
    }
    var QJ = p1.unstable_now, ML = 0, X5 = -1, oW = -1, J5 = -1, s2 = !1, $5 = !1;
    function DL() {
      return s2;
    }
    function W_() {
      $5 = !0;
    }
    function K_() {
      s2 = !1, $5 = !1;
    }
    function H_() {
      s2 = $5, $5 = !1;
    }
    function kL() {
      return ML;
    }
    function RL() {
      ML = QJ();
    }
    function o2(Z) {
      if (oW = QJ(), Z.actualStartTime < 0)
        Z.actualStartTime = QJ();
    }
    function jL(Z) {
      oW = -1;
    }
    function Y5(Z, X) {
      if (oW >= 0) {
        var $ = QJ() - oW;
        if (Z.actualDuration += $, X)
          Z.selfBaseDuration = $;
        oW = -1;
      }
    }
    function _X(Z) {
      if (X5 >= 0) {
        var X = QJ() - X5;
        X5 = -1;
        var $ = Z.return;
        while ($ !== null) {
          switch ($.tag) {
            case w:
              var q = $.stateNode;
              q.effectDuration += X;
              return;
            case J0:
              var H = $.stateNode;
              H.effectDuration += X;
              return;
          }
          $ = $.return;
        }
      }
    }
    function a2(Z) {
      if (J5 >= 0) {
        var X = QJ() - J5;
        J5 = -1;
        var $ = Z.return;
        while ($ !== null) {
          switch ($.tag) {
            case w:
              var q = $.stateNode;
              if (q !== null)
                q.passiveEffectDuration += X;
              return;
            case J0:
              var H = $.stateNode;
              if (H !== null)
                H.passiveEffectDuration += X;
              return;
          }
          $ = $.return;
        }
      }
    }
    function TX() {
      X5 = QJ();
    }
    function r2() {
      J5 = QJ();
    }
    function i2(Z) {
      var X = Z.child;
      while (X)
        Z.actualDuration += X.actualDuration, X = X.sibling;
    }
    function aZ(Z, X) {
      if (Z && Z.defaultProps) {
        var $ = K1({}, X), q = Z.defaultProps;
        for (var H in q)
          if ($[H] === void 0)
            $[H] = q[H];
        return $;
      }
      return X;
    }
    var t2 = {}, e2, Qz, Zz, Xz, Jz, BL, q5, $z, Yz, qz, aW;
    {
      e2 = /* @__PURE__ */ new Set, Qz = /* @__PURE__ */ new Set, Zz = /* @__PURE__ */ new Set, Xz = /* @__PURE__ */ new Set, $z = /* @__PURE__ */ new Set, Jz = /* @__PURE__ */ new Set, Yz = /* @__PURE__ */ new Set, qz = /* @__PURE__ */ new Set, aW = /* @__PURE__ */ new Set;
      var CL = /* @__PURE__ */ new Set;
      q5 = function(Z, X) {
        if (Z === null || typeof Z === "function")
          return;
        var $ = X + "_" + Z;
        if (!CL.has($))
          CL.add($), K("%s(...): Expected the last optional `callback` argument to be a function. Instead received: %s.", X, Z);
      }, BL = function(Z, X) {
        if (X === void 0) {
          var $ = h0(Z) || "Component";
          if (!Jz.has($))
            Jz.add($), K("%s.getDerivedStateFromProps(): A valid state object (or null) must be returned. You have returned undefined.", $);
        }
      }, Object.defineProperty(t2, "_processChildContext", {
        enumerable: !1,
        value: function() {
          throw new Error("_processChildContext is not available in React 16+. This likely means you have multiple copies of React and are attempting to nest a React 15 tree inside a React 16 tree using unstable_renderSubtreeIntoContainer, which isn't supported. Try to make sure you have only one copy of React (and ideally, switch to ReactDOM.createPortal).");
        }
      }), Object.freeze(t2);
    }
    function Wz(Z, X, $, q) {
      var H = Z.memoizedState, G = $(q, H);
      {
        if (Z.mode & j6) {
          F8(!0);
          try {
            G = $(q, H);
          } finally {
            F8(!1);
          }
        }
        BL(X, G);
      }
      var E = G === null || G === void 0 ? H : K1({}, H, G);
      if (Z.memoizedState = E, Z.lanes === n) {
        var U = Z.updateQueue;
        U.baseState = E;
      }
    }
    var Kz = {
      isMounted: ZB,
      enqueueSetState: function(Z, X, $) {
        var q = qY(Z), H = UQ(), G = $J(q), E = z4(H, G);
        if (E.payload = X, $ !== void 0 && $ !== null)
          q5($, "setState"), E.callback = $;
        var U = r4(q, E, G);
        if (U !== null)
          Z8(U, q, G, H), g9(U, q, G);
        f7(q, G);
      },
      enqueueReplaceState: function(Z, X, $) {
        var q = qY(Z), H = UQ(), G = $J(q), E = z4(H, G);
        if (E.tag = dA, E.payload = X, $ !== void 0 && $ !== null)
          q5($, "replaceState"), E.callback = $;
        var U = r4(q, E, G);
        if (U !== null)
          Z8(U, q, G, H), g9(U, q, G);
        f7(q, G);
      },
      enqueueForceUpdate: function(Z, X) {
        var $ = qY(Z), q = UQ(), H = $J($), G = z4(q, H);
        if (G.tag = I9, X !== void 0 && X !== null)
          q5(X, "forceUpdate"), G.callback = X;
        var E = r4($, G, H);
        if (E !== null)
          Z8(E, $, H, q), g9(E, $, H);
        TB($, H);
      }
    };
    function VL(Z, X, $, q, H, G, E) {
      var U = Z.stateNode;
      if (typeof U.shouldComponentUpdate === "function") {
        var P = U.shouldComponentUpdate(q, G, E);
        {
          if (Z.mode & j6) {
            F8(!0);
            try {
              P = U.shouldComponentUpdate(q, G, E);
            } finally {
              F8(!1);
            }
          }
          if (P === void 0)
            K("%s.shouldComponentUpdate(): Returned undefined instead of a boolean value. Make sure to return true or false.", h0(X) || "Component");
        }
        return P;
      }
      if (X.prototype && X.prototype.isPureReactComponent)
        return !AW($, q) || !AW(H, G);
      return !0;
    }
    function G_(Z, X, $) {
      var q = Z.stateNode;
      {
        var H = h0(X) || "Component", G = q.render;
        if (!G)
          if (X.prototype && typeof X.prototype.render === "function")
            K("%s(...): No `render` method found on the returned component instance: did you accidentally return an object from the constructor?", H);
          else
            K("%s(...): No `render` method found on the returned component instance: you may have forgotten to define `render`.", H);
        if (q.getInitialState && !q.getInitialState.isReactClassApproved && !q.state)
          K("getInitialState was defined on %s, a plain JavaScript class. This is only supported for classes created using React.createClass. Did you mean to define a state property instead?", H);
        if (q.getDefaultProps && !q.getDefaultProps.isReactClassApproved)
          K("getDefaultProps was defined on %s, a plain JavaScript class. This is only supported for classes created using React.createClass. Use a static property to define defaultProps instead.", H);
        if (q.propTypes)
          K("propTypes was defined as an instance property on %s. Use a static property to define propTypes instead.", H);
        if (q.contextType)
          K("contextType was defined as an instance property on %s. Use a static property to define contextType instead.", H);
        {
          if (X.childContextTypes && !aW.has(X) && (Z.mode & j6) === B0)
            aW.add(X), K(`%s uses the legacy childContextTypes API which is no longer supported and will be removed in the next major release. Use React.createContext() instead

.Learn more about this warning here: https://reactjs.org/link/legacy-context`, H);
          if (X.contextTypes && !aW.has(X) && (Z.mode & j6) === B0)
            aW.add(X), K(`%s uses the legacy contextTypes API which is no longer supported and will be removed in the next major release. Use React.createContext() with static contextType instead.

Learn more about this warning here: https://reactjs.org/link/legacy-context`, H);
          if (q.contextTypes)
            K("contextTypes was defined as an instance property on %s. Use a static property to define contextTypes instead.", H);
          if (X.contextType && X.contextTypes && !Yz.has(X))
            Yz.add(X), K("%s declares both contextTypes and contextType static properties. The legacy contextTypes property will be ignored.", H);
        }
        if (typeof q.componentShouldUpdate === "function")
          K("%s has a method called componentShouldUpdate(). Did you mean shouldComponentUpdate()? The name is phrased as a question because the function is expected to return a value.", H);
        if (X.prototype && X.prototype.isPureReactComponent && typeof q.shouldComponentUpdate !== "undefined")
          K("%s has a method called shouldComponentUpdate(). shouldComponentUpdate should not be used when extending React.PureComponent. Please extend React.Component if shouldComponentUpdate is used.", h0(X) || "A pure component");
        if (typeof q.componentDidUnmount === "function")
          K("%s has a method called componentDidUnmount(). But there is no such lifecycle method. Did you mean componentWillUnmount()?", H);
        if (typeof q.componentDidReceiveProps === "function")
          K("%s has a method called componentDidReceiveProps(). But there is no such lifecycle method. If you meant to update the state in response to changing props, use componentWillReceiveProps(). If you meant to fetch data or run side-effects or mutations after React has updated the UI, use componentDidUpdate().", H);
        if (typeof q.componentWillRecieveProps === "function")
          K("%s has a method called componentWillRecieveProps(). Did you mean componentWillReceiveProps()?", H);
        if (typeof q.UNSAFE_componentWillRecieveProps === "function")
          K("%s has a method called UNSAFE_componentWillRecieveProps(). Did you mean UNSAFE_componentWillReceiveProps()?", H);
        var E = q.props !== $;
        if (q.props !== void 0 && E)
          K("%s(...): When calling super() in `%s`, make sure to pass up the same props that your component's constructor was passed.", H, H);
        if (q.defaultProps)
          K("Setting defaultProps as an instance property on %s is not supported and will be ignored. Instead, define defaultProps as a static property on %s.", H, H);
        if (typeof q.getSnapshotBeforeUpdate === "function" && typeof q.componentDidUpdate !== "function" && !Zz.has(X))
          Zz.add(X), K("%s: getSnapshotBeforeUpdate() should be used with componentDidUpdate(). This component defines getSnapshotBeforeUpdate() only.", h0(X));
        if (typeof q.getDerivedStateFromProps === "function")
          K("%s: getDerivedStateFromProps() is defined as an instance method and will be ignored. Instead, declare it as a static method.", H);
        if (typeof q.getDerivedStateFromError === "function")
          K("%s: getDerivedStateFromError() is defined as an instance method and will be ignored. Instead, declare it as a static method.", H);
        if (typeof X.getSnapshotBeforeUpdate === "function")
          K("%s: getSnapshotBeforeUpdate() is defined as a static method and will be ignored. Instead, declare it as an instance method.", H);
        var U = q.state;
        if (U && (typeof U !== "object" || S1(U)))
          K("%s.state: must be set to an object or null", H);
        if (typeof q.getChildContext === "function" && typeof X.childContextTypes !== "object")
          K("%s.getChildContext(): childContextTypes must be defined in order to use getChildContext().", H);
      }
    }
    function SL(Z, X) {
      X.updater = Kz, Z.stateNode = X, rj(X, Z), X._reactInternalInstance = t2;
    }
    function IL(Z, X, $) {
      var q = !1, H = rQ, G = rQ, E = X.contextType;
      if ("contextType" in X) {
        var U = E === null || E !== void 0 && E.$$typeof === fZ && E._context === void 0;
        if (!U && !qz.has(X)) {
          qz.add(X);
          var P = "";
          if (E === void 0)
            P = " However, it is set to undefined. This can be caused by a typo or by mixing up named and default imports. This can also happen due to a circular dependency, so try moving the createContext() call to a separate file.";
          else if (typeof E !== "object")
            P = " However, it is set to a " + typeof E + ".";
          else if (E.$$typeof === HQ)
            P = " Did you accidentally pass the Context.Provider instead?";
          else if (E._context !== void 0)
            P = " Did you accidentally pass the Context.Consumer instead?";
          else
            P = " However, it is set to an object with keys {" + Object.keys(E).join(", ") + "}.";
          K("%s defines an invalid contextType. contextType should point to the Context object returned by React.createContext().%s", h0(X) || "Component", P);
        }
      }
      if (typeof E === "object" && E !== null)
        G = b6(E);
      else {
        H = kY(Z, X, !0);
        var O = X.contextTypes;
        q = O !== null && O !== void 0, G = q ? RY(Z, H) : rQ;
      }
      var k = new X($, G);
      if (Z.mode & j6) {
        F8(!0);
        try {
          k = new X($, G);
        } finally {
          F8(!1);
        }
      }
      var C = Z.memoizedState = k.state !== null && k.state !== void 0 ? k.state : null;
      SL(Z, k);
      {
        if (typeof X.getDerivedStateFromProps === "function" && C === null) {
          var B = h0(X) || "Component";
          if (!Qz.has(B))
            Qz.add(B), K("`%s` uses `getDerivedStateFromProps` but its initial state is %s. This is not recommended. Instead, define the initial state by assigning an object to `this.state` in the constructor of `%s`. This ensures that `getDerivedStateFromProps` arguments have a consistent shape.", B, k.state === null ? "null" : "undefined", B);
        }
        if (typeof X.getDerivedStateFromProps === "function" || typeof k.getSnapshotBeforeUpdate === "function") {
          var v = null, h = null, f = null;
          if (typeof k.componentWillMount === "function" && k.componentWillMount.__suppressDeprecationWarning !== !0)
            v = "componentWillMount";
          else if (typeof k.UNSAFE_componentWillMount === "function")
            v = "UNSAFE_componentWillMount";
          if (typeof k.componentWillReceiveProps === "function" && k.componentWillReceiveProps.__suppressDeprecationWarning !== !0)
            h = "componentWillReceiveProps";
          else if (typeof k.UNSAFE_componentWillReceiveProps === "function")
            h = "UNSAFE_componentWillReceiveProps";
          if (typeof k.componentWillUpdate === "function" && k.componentWillUpdate.__suppressDeprecationWarning !== !0)
            f = "componentWillUpdate";
          else if (typeof k.UNSAFE_componentWillUpdate === "function")
            f = "UNSAFE_componentWillUpdate";
          if (v !== null || h !== null || f !== null) {
            var q0 = h0(X) || "Component", k0 = typeof X.getDerivedStateFromProps === "function" ? "getDerivedStateFromProps()" : "getSnapshotBeforeUpdate()";
            if (!Xz.has(q0))
              Xz.add(q0), K(`Unsafe legacy lifecycles will not be called for components using new component APIs.

%s uses %s but also contains the following legacy lifecycles:%s%s%s

The above lifecycles should be removed. Learn more about this warning here:
https://reactjs.org/link/unsafe-component-lifecycles`, q0, k0, v !== null ? `
  ` + v : "", h !== null ? `
  ` + h : "", f !== null ? `
  ` + f : "");
          }
        }
      }
      if (q)
        OA(Z, H, G);
      return k;
    }
    function z_(Z, X) {
      var $ = X.state;
      if (typeof X.componentWillMount === "function")
        X.componentWillMount();
      if (typeof X.UNSAFE_componentWillMount === "function")
        X.UNSAFE_componentWillMount();
      if ($ !== X.state)
        K("%s.componentWillMount(): Assigning directly to this.state is deprecated (except inside a component's constructor). Use setState instead.", V0(Z) || "Component"), Kz.enqueueReplaceState(X, X.state, null);
    }
    function _L(Z, X, $, q) {
      var H = X.state;
      if (typeof X.componentWillReceiveProps === "function")
        X.componentWillReceiveProps($, q);
      if (typeof X.UNSAFE_componentWillReceiveProps === "function")
        X.UNSAFE_componentWillReceiveProps($, q);
      if (X.state !== H) {
        {
          var G = V0(Z) || "Component";
          if (!e2.has(G))
            e2.add(G), K("%s.componentWillReceiveProps(): Assigning directly to this.state is deprecated (except inside a component's constructor). Use setState instead.", G);
        }
        Kz.enqueueReplaceState(X, X.state, null);
      }
    }
    function Hz(Z, X, $, q) {
      G_(Z, X, $);
      var H = Z.stateNode;
      H.props = $, H.state = Z.memoizedState, H.refs = {}, A2(Z);
      var G = X.contextType;
      if (typeof G === "object" && G !== null)
        H.context = b6(G);
      else {
        var E = kY(Z, X, !0);
        H.context = RY(Z, E);
      }
      {
        if (H.state === $) {
          var U = h0(X) || "Component";
          if (!$z.has(U))
            $z.add(U), K("%s: It is not recommended to assign props directly to state because updates to props won't be reflected in state. In most cases, it is better to use props directly.", U);
        }
        if (Z.mode & j6)
          nZ.recordLegacyContextWarning(Z, H);
        nZ.recordUnsafeLifecycleWarnings(Z, H);
      }
      H.state = Z.memoizedState;
      var P = X.getDerivedStateFromProps;
      if (typeof P === "function")
        Wz(Z, X, P, $), H.state = Z.memoizedState;
      if (typeof X.getDerivedStateFromProps !== "function" && typeof H.getSnapshotBeforeUpdate !== "function" && (typeof H.UNSAFE_componentWillMount === "function" || typeof H.componentWillMount === "function"))
        z_(Z, H), x9(Z, $, H, q), H.state = Z.memoizedState;
      if (typeof H.componentDidMount === "function") {
        var O = O1;
        if (O |= rJ, (Z.mode & RX) !== B0)
          O |= Z4;
        Z.flags |= O;
      }
    }
    function N_(Z, X, $, q) {
      var { stateNode: H, memoizedProps: G } = Z;
      H.props = G;
      var E = H.context, U = X.contextType, P = rQ;
      if (typeof U === "object" && U !== null)
        P = b6(U);
      else {
        var O = kY(Z, X, !0);
        P = RY(Z, O);
      }
      var k = X.getDerivedStateFromProps, C = typeof k === "function" || typeof H.getSnapshotBeforeUpdate === "function";
      if (!C && (typeof H.UNSAFE_componentWillReceiveProps === "function" || typeof H.componentWillReceiveProps === "function")) {
        if (G !== $ || E !== P)
          _L(Z, H, $, P);
      }
      nA();
      var B = Z.memoizedState, v = H.state = B;
      if (x9(Z, $, H, q), v = Z.memoizedState, G === $ && B === v && !U9() && !v9()) {
        if (typeof H.componentDidMount === "function") {
          var h = O1;
          if (h |= rJ, (Z.mode & RX) !== B0)
            h |= Z4;
          Z.flags |= h;
        }
        return !1;
      }
      if (typeof k === "function")
        Wz(Z, X, k, $), v = Z.memoizedState;
      var f = v9() || VL(Z, X, G, $, B, v, P);
      if (f) {
        if (!C && (typeof H.UNSAFE_componentWillMount === "function" || typeof H.componentWillMount === "function")) {
          if (typeof H.componentWillMount === "function")
            H.componentWillMount();
          if (typeof H.UNSAFE_componentWillMount === "function")
            H.UNSAFE_componentWillMount();
        }
        if (typeof H.componentDidMount === "function") {
          var q0 = O1;
          if (q0 |= rJ, (Z.mode & RX) !== B0)
            q0 |= Z4;
          Z.flags |= q0;
        }
      } else {
        if (typeof H.componentDidMount === "function") {
          var k0 = O1;
          if (k0 |= rJ, (Z.mode & RX) !== B0)
            k0 |= Z4;
          Z.flags |= k0;
        }
        Z.memoizedProps = $, Z.memoizedState = v;
      }
      return H.props = $, H.state = v, H.context = P, f;
    }
    function E_(Z, X, $, q, H) {
      var G = X.stateNode;
      lA(Z, X);
      var E = X.memoizedProps, U = X.type === X.elementType ? E : aZ(X.type, E);
      G.props = U;
      var P = X.pendingProps, O = G.context, k = $.contextType, C = rQ;
      if (typeof k === "object" && k !== null)
        C = b6(k);
      else {
        var B = kY(X, $, !0);
        C = RY(X, B);
      }
      var v = $.getDerivedStateFromProps, h = typeof v === "function" || typeof G.getSnapshotBeforeUpdate === "function";
      if (!h && (typeof G.UNSAFE_componentWillReceiveProps === "function" || typeof G.componentWillReceiveProps === "function")) {
        if (E !== P || O !== C)
          _L(X, G, q, C);
      }
      nA();
      var f = X.memoizedState, q0 = G.state = f;
      if (x9(X, q, G, H), q0 = X.memoizedState, E === P && f === q0 && !U9() && !v9() && !v0) {
        if (typeof G.componentDidUpdate === "function") {
          if (E !== Z.memoizedProps || f !== Z.memoizedState)
            X.flags |= O1;
        }
        if (typeof G.getSnapshotBeforeUpdate === "function") {
          if (E !== Z.memoizedProps || f !== Z.memoizedState)
            X.flags |= oJ;
        }
        return !1;
      }
      if (typeof v === "function")
        Wz(X, $, v, q), q0 = X.memoizedState;
      var k0 = v9() || VL(X, $, U, q, f, q0, C) || v0;
      if (k0) {
        if (!h && (typeof G.UNSAFE_componentWillUpdate === "function" || typeof G.componentWillUpdate === "function")) {
          if (typeof G.componentWillUpdate === "function")
            G.componentWillUpdate(q, q0, C);
          if (typeof G.UNSAFE_componentWillUpdate === "function")
            G.UNSAFE_componentWillUpdate(q, q0, C);
        }
        if (typeof G.componentDidUpdate === "function")
          X.flags |= O1;
        if (typeof G.getSnapshotBeforeUpdate === "function")
          X.flags |= oJ;
      } else {
        if (typeof G.componentDidUpdate === "function") {
          if (E !== Z.memoizedProps || f !== Z.memoizedState)
            X.flags |= O1;
        }
        if (typeof G.getSnapshotBeforeUpdate === "function") {
          if (E !== Z.memoizedProps || f !== Z.memoizedState)
            X.flags |= oJ;
        }
        X.memoizedProps = q, X.memoizedState = q0;
      }
      return G.props = q, G.state = q0, G.context = C, k0;
    }
    function U$(Z, X) {
      return {
        value: Z,
        source: X,
        stack: _0(X),
        digest: null
      };
    }
    function Gz(Z, X, $) {
      return {
        value: Z,
        source: null,
        stack: $ != null ? $ : null,
        digest: X != null ? X : null
      };
    }
    function F_(Z, X) {
      return !0;
    }
    function zz(Z, X) {
      try {
        var $ = F_(Z, X);
        if ($ === !1)
          return;
        var { value: q, source: H, stack: G } = X, E = G !== null ? G : "";
        if (q != null && q._suppressLogging) {
          if (Z.tag === F)
            return;
          console.error(q);
        }
        var U = H ? V0(H) : null, P = U ? "The above error occurred in the <" + U + "> component:" : "The above error occurred in one of your React components:", O;
        if (Z.tag === w)
          O = `Consider adding an error boundary to your tree to customize error handling behavior.
Visit https://reactjs.org/link/error-boundaries to learn more about error boundaries.`;
        else {
          var k = V0(Z) || "Anonymous";
          O = "React will try to recreate this component tree from scratch " + ("using the error boundary you provided, " + k + ".");
        }
        var C = P + `
` + E + `

` + ("" + O);
        console.error(C);
      } catch (B) {
        setTimeout(function() {
          throw B;
        });
      }
    }
    var U_ = typeof WeakMap === "function" ? WeakMap : Map;
    function TL(Z, X, $) {
      var q = z4(J6, $);
      q.tag = U2, q.payload = {
        element: null
      };
      var H = X.value;
      return q.callback = function() {
        Ng(H), zz(Z, X);
      }, q;
    }
    function Nz(Z, X, $) {
      var q = z4(J6, $);
      q.tag = U2;
      var H = Z.type.getDerivedStateFromError;
      if (typeof H === "function") {
        var G = X.value;
        q.payload = function() {
          return H(G);
        }, q.callback = function() {
          dO(Z), zz(Z, X);
        };
      }
      var E = Z.stateNode;
      if (E !== null && typeof E.componentDidCatch === "function")
        q.callback = function U() {
          if (dO(Z), zz(Z, X), typeof H !== "function")
            Gg(this);
          var { value: P, stack: O } = X;
          if (this.componentDidCatch(P, {
            componentStack: O !== null ? O : ""
          }), typeof H !== "function") {
            if (!nQ(Z.lanes, b0))
              K("%s: Error boundaries should implement getDerivedStateFromError(). In that method, return a state update to display an error message or fallback UI.", V0(Z) || "Unknown");
          }
        };
      return q;
    }
    function gL(Z, X, $) {
      var q = Z.pingCache, H;
      if (q === null)
        q = Z.pingCache = new U_, H = /* @__PURE__ */ new Set, q.set(X, H);
      else if (H = q.get(X), H === void 0)
        H = /* @__PURE__ */ new Set, q.set(X, H);
      if (!H.has($)) {
        H.add($);
        var G = Eg.bind(null, Z, X, $);
        if (cZ)
          N3(Z, $);
        X.then(G, G);
      }
    }
    function P_(Z, X, $, q) {
      var H = Z.updateQueue;
      if (H === null) {
        var G = /* @__PURE__ */ new Set;
        G.add($), Z.updateQueue = G;
      } else
        H.add($);
    }
    function A_(Z, X) {
      var $ = Z.tag;
      if ((Z.mode & A1) === B0 && ($ === N || $ === r || $ === $0)) {
        var q = Z.alternate;
        if (q)
          Z.updateQueue = q.updateQueue, Z.memoizedState = q.memoizedState, Z.lanes = q.lanes;
        else
          Z.updateQueue = null, Z.memoizedState = null;
      }
    }
    function xL(Z) {
      var X = Z;
      do {
        if (X.tag === l && tI(X))
          return X;
        X = X.return;
      } while (X !== null);
      return null;
    }
    function vL(Z, X, $, q, H) {
      if ((Z.mode & A1) === B0) {
        if (Z === X)
          Z.flags |= NQ;
        else {
          if (Z.flags |= I1, $.flags |= _7, $.flags &= ~(ij | oq), $.tag === F) {
            var G = $.alternate;
            if (G === null)
              $.tag = c0;
            else {
              var E = z4(J6, b0);
              E.tag = I9, r4($, E, b0);
            }
          }
          $.lanes = Q1($.lanes, b0);
        }
        return Z;
      }
      return Z.flags |= NQ, Z.lanes = H, Z;
    }
    function L_(Z, X, $, q, H) {
      if ($.flags |= oq, cZ)
        N3(Z, H);
      if (q !== null && typeof q === "object" && typeof q.then === "function") {
        var G = q;
        if (A_($), S8() && $.mode & A1)
          BA();
        var E = xL(X);
        if (E !== null) {
          if (E.flags &= ~eX, vL(E, X, $, Z, H), E.mode & A1)
            gL(Z, G, H);
          P_(E, Z, G);
          return;
        } else {
          if (!uB(H)) {
            gL(Z, G, H), nz();
            return;
          }
          var U = new Error("A component suspended while responding to synchronous input. This will cause the UI to be replaced with a loading indicator. To fix, updates that suspend should be wrapped with startTransition.");
          q = U;
        }
      } else if (S8() && $.mode & A1) {
        BA();
        var P = xL(X);
        if (P !== null) {
          if ((P.flags & NQ) === S0)
            P.flags |= eX;
          vL(P, X, $, Z, H), J2(U$(q, $));
          return;
        }
      }
      q = U$(q, $), Xg(q);
      var O = X;
      do {
        switch (O.tag) {
          case w: {
            var k = q;
            O.flags |= NQ;
            var C = XW(H);
            O.lanes = Q1(O.lanes, C);
            var B = TL(O, k, C);
            L2(O, B);
            return;
          }
          case F:
            var v = q, h = O.type, f = O.stateNode;
            if ((O.flags & I1) === S0 && (typeof h.getDerivedStateFromError === "function" || f !== null && typeof f.componentDidCatch === "function" && !vO(f))) {
              O.flags |= NQ;
              var q0 = XW(H);
              O.lanes = Q1(O.lanes, q0);
              var k0 = Nz(O, v, q0);
              L2(O, k0);
              return;
            }
            break;
        }
        O = O.return;
      } while (O !== null);
    }
    function O_() {
      return null;
    }
    var rW = Q.ReactCurrentOwner, rZ = !1, Ez, iW, Fz, Uz, Pz, P$, Az, W5, tW;
    Ez = {}, iW = {}, Fz = {}, Uz = {}, Pz = {}, P$ = !1, Az = {}, W5 = {}, tW = {};
    function EQ(Z, X, $, q) {
      if (Z === null)
        X.child = fA(X, null, $, q);
      else
        X.child = VY(X, Z.child, $, q);
    }
    function w_(Z, X, $, q) {
      X.child = VY(X, Z.child, null, q), X.child = VY(X, null, $, q);
    }
    function hL(Z, X, $, q, H) {
      if (X.type !== X.elementType) {
        var G = $.propTypes;
        if (G)
          dZ(G, q, "prop", h0($));
      }
      var E = $.render, U = X.ref, P, O;
      IY(X, H), rq(X);
      {
        if (rW.current = X, dQ(!0), P = hY(Z, X, E, q, U, H), O = yY(), X.mode & j6) {
          F8(!0);
          try {
            P = hY(Z, X, E, q, U, H), O = yY();
          } finally {
            F8(!1);
          }
        }
        dQ(!1);
      }
      if (HY(), Z !== null && !rZ)
        return tA(Z, X, H), N4(Z, X, H);
      if (S8() && O)
        iG(X);
      return X.flags |= WY, EQ(Z, X, P, H), X.child;
    }
    function yL(Z, X, $, q, H) {
      if (Z === null) {
        var G = $.type;
        if (Ig(G) && $.compare === null && $.defaultProps === void 0) {
          var E = G;
          return E = lY(G), X.tag = $0, X.type = E, wz(X, G), fL(Z, X, E, q, H);
        }
        {
          var U = G.propTypes;
          if (U)
            dZ(U, q, "prop", h0(G));
          if ($.defaultProps !== void 0) {
            var P = h0(G) || "Unknown";
            if (!tW[P])
              K("%s: Support for defaultProps will be removed from memo components in a future major release. Use JavaScript default parameters instead.", P), tW[P] = !0;
          }
        }
        var O = JN($.type, null, q, X, X.mode, H);
        return O.ref = X.ref, O.return = X, X.child = O, O;
      }
      {
        var k = $.type, C = k.propTypes;
        if (C)
          dZ(C, q, "prop", h0(k));
      }
      var B = Z.child, v = Bz(Z, H);
      if (!v) {
        var h = B.memoizedProps, f = $.compare;
        if (f = f !== null ? f : AW, f(h, q) && Z.ref === X.ref)
          return N4(Z, X, H);
      }
      X.flags |= WY;
      var q0 = M$(B, q);
      return q0.ref = X.ref, q0.return = X, X.child = q0, q0;
    }
    function fL(Z, X, $, q, H) {
      if (X.type !== X.elementType) {
        var G = X.elementType;
        if (G.$$typeof === n6) {
          var E = G, U = E._payload, P = E._init;
          try {
            G = P(U);
          } catch (C) {
            G = null;
          }
          var O = G && G.propTypes;
          if (O)
            dZ(O, q, "prop", h0(G));
        }
      }
      if (Z !== null) {
        var k = Z.memoizedProps;
        if (AW(k, q) && Z.ref === X.ref && X.type === Z.type) {
          if (rZ = !1, X.pendingProps = q = k, !Bz(Z, H))
            return X.lanes = Z.lanes, N4(Z, X, H);
          else if ((Z.flags & _7) !== S0)
            rZ = !0;
        }
      }
      return Lz(Z, X, $, q, H);
    }
    function mL(Z, X, $) {
      var q = X.pendingProps, H = q.children, G = Z !== null ? Z.memoizedState : null;
      if (q.mode === "hidden" || n1)
        if ((X.mode & A1) === B0) {
          var E = {
            baseLanes: n,
            cachePool: null,
            transitions: null
          };
          X.memoizedState = E, w5(X, $);
        } else if (!nQ($, lQ)) {
          var U = null, P;
          if (G !== null) {
            var O = G.baseLanes;
            P = Q1(O, $);
          } else
            P = $;
          X.lanes = X.childLanes = bK(lQ);
          var k = {
            baseLanes: P,
            cachePool: U,
            transitions: null
          };
          return X.memoizedState = k, X.updateQueue = null, w5(X, P), null;
        } else {
          var C = {
            baseLanes: n,
            cachePool: null,
            transitions: null
          };
          X.memoizedState = C;
          var B = G !== null ? G.baseLanes : $;
          w5(X, B);
        }
      else {
        var v;
        if (G !== null)
          v = Q1(G.baseLanes, $), X.memoizedState = null;
        else
          v = $;
        w5(X, v);
      }
      return EQ(Z, X, H, $), X.child;
    }
    function M_(Z, X, $) {
      var q = X.pendingProps;
      return EQ(Z, X, q, $), X.child;
    }
    function D_(Z, X, $) {
      var q = X.pendingProps.children;
      return EQ(Z, X, q, $), X.child;
    }
    function k_(Z, X, $) {
      {
        X.flags |= O1;
        {
          var q = X.stateNode;
          q.effectDuration = 0, q.passiveEffectDuration = 0;
        }
      }
      var H = X.pendingProps, G = H.children;
      return EQ(Z, X, G, $), X.child;
    }
    function bL(Z, X) {
      var $ = X.ref;
      if (Z === null && $ !== null || Z !== null && Z.ref !== $)
        X.flags |= f4, X.flags |= T7;
    }
    function Lz(Z, X, $, q, H) {
      if (X.type !== X.elementType) {
        var G = $.propTypes;
        if (G)
          dZ(G, q, "prop", h0($));
      }
      var E;
      {
        var U = kY(X, $, !0);
        E = RY(X, U);
      }
      var P, O;
      IY(X, H), rq(X);
      {
        if (rW.current = X, dQ(!0), P = hY(Z, X, $, q, E, H), O = yY(), X.mode & j6) {
          F8(!0);
          try {
            P = hY(Z, X, $, q, E, H), O = yY();
          } finally {
            F8(!1);
          }
        }
        dQ(!1);
      }
      if (HY(), Z !== null && !rZ)
        return tA(Z, X, H), N4(Z, X, H);
      if (S8() && O)
        iG(X);
      return X.flags |= WY, EQ(Z, X, P, H), X.child;
    }
    function uL(Z, X, $, q, H) {
      {
        switch (lg(X)) {
          case !1: {
            var { stateNode: G, type: E } = X, U = new E(X.memoizedProps, G.context), P = U.state;
            G.updater.enqueueSetState(G, P, null);
            break;
          }
          case !0: {
            X.flags |= I1, X.flags |= NQ;
            var O = new Error("Simulated error coming from DevTools"), k = XW(H);
            X.lanes = Q1(X.lanes, k);
            var C = Nz(X, U$(O, X), k);
            L2(X, C);
            break;
          }
        }
        if (X.type !== X.elementType) {
          var B = $.propTypes;
          if (B)
            dZ(B, q, "prop", h0($));
        }
      }
      var v;
      if (CX($))
        v = !0, A9(X);
      else
        v = !1;
      IY(X, H);
      var h = X.stateNode, f;
      if (h === null)
        H5(Z, X), IL(X, $, q), Hz(X, $, q, H), f = !0;
      else if (Z === null)
        f = N_(X, $, q, H);
      else
        f = E_(Z, X, $, q, H);
      var q0 = Oz(Z, X, $, f, v, H);
      {
        var k0 = X.stateNode;
        if (f && k0.props !== q) {
          if (!P$)
            K("It looks like %s is reassigning its own `this.props` while rendering. This is not supported and can lead to confusing bugs.", V0(X) || "a component");
          P$ = !0;
        }
      }
      return q0;
    }
    function Oz(Z, X, $, q, H, G) {
      bL(Z, X);
      var E = (X.flags & I1) !== S0;
      if (!q && !E) {
        if (H)
          DA(X, $, !1);
        return N4(Z, X, G);
      }
      var U = X.stateNode;
      rW.current = X;
      var P;
      if (E && typeof $.getDerivedStateFromError !== "function")
        P = null, jL();
      else {
        rq(X);
        {
          if (dQ(!0), P = U.render(), X.mode & j6) {
            F8(!0);
            try {
              U.render();
            } finally {
              F8(!1);
            }
          }
          dQ(!1);
        }
        HY();
      }
      if (X.flags |= WY, Z !== null && E)
        w_(Z, X, P, G);
      else
        EQ(Z, X, P, G);
      if (X.memoizedState = U.state, H)
        DA(X, $, !0);
      return X.child;
    }
    function cL(Z) {
      var X = Z.stateNode;
      if (X.pendingContext)
        wA(Z, X.pendingContext, X.pendingContext !== X.context);
      else if (X.context)
        wA(Z, X.context, !1);
      O2(Z, X.containerInfo);
    }
    function R_(Z, X, $) {
      if (cL(X), Z === null)
        throw new Error("Should have a current fiber. This is a bug in React.");
      var { pendingProps: q, memoizedState: H } = X, G = H.element;
      lA(Z, X), x9(X, q, null, $);
      var { memoizedState: E, stateNode: U } = X, P = E.element;
      if (H.isDehydrated) {
        var O = {
          element: P,
          isDehydrated: !1,
          cache: E.cache,
          pendingSuspenseBoundaries: E.pendingSuspenseBoundaries,
          transitions: E.transitions
        }, k = X.updateQueue;
        if (k.baseState = O, X.memoizedState = O, X.flags & eX) {
          var C = U$(new Error("There was an error while hydrating. Because the error happened outside of a Suspense boundary, the entire root will switch to client rendering."), X);
          return pL(Z, X, P, $, C);
        } else if (P !== G) {
          var B = U$(new Error("This root received an early update, before anything was able hydrate. Switched the entire root to client rendering."), X);
          return pL(Z, X, P, $, B);
        } else {
          VI(X);
          var v = fA(X, null, P, $);
          X.child = v;
          var h = v;
          while (h)
            h.flags = h.flags & ~m6 | Q4, h = h.sibling;
        }
      } else {
        if (CY(), P === G)
          return N4(Z, X, $);
        EQ(Z, X, P, $);
      }
      return X.child;
    }
    function pL(Z, X, $, q, H) {
      return CY(), J2(H), X.flags |= eX, EQ(Z, X, $, q), X.child;
    }
    function j_(Z, X, $) {
      if (aA(X), Z === null)
        X2(X);
      var { type: q, pendingProps: H } = X, G = Z !== null ? Z.memoizedProps : null, E = H.children, U = fG(q, H);
      if (U)
        E = null;
      else if (G !== null && fG(q, G))
        X.flags |= sq;
      return bL(Z, X), EQ(Z, X, E, $), X.child;
    }
    function B_(Z, X) {
      if (Z === null)
        X2(X);
      return null;
    }
    function C_(Z, X, $, q) {
      H5(Z, X);
      var H = X.pendingProps, G = $, E = G._payload, U = G._init, P = U(E);
      X.type = P;
      var O = X.tag = _g(P), k = aZ(P, H), C;
      switch (O) {
        case N:
          return wz(X, P), X.type = P = lY(P), C = Lz(null, X, P, k, q), C;
        case F:
          return X.type = P = iz(P), C = uL(null, X, P, k, q), C;
        case r:
          return X.type = P = tz(P), C = hL(null, X, P, k, q), C;
        case t: {
          if (X.type !== X.elementType) {
            var B = P.propTypes;
            if (B)
              dZ(B, k, "prop", h0(P));
          }
          return C = yL(null, X, P, aZ(P.type, k), q), C;
        }
      }
      var v = "";
      if (P !== null && typeof P === "object" && P.$$typeof === n6)
        v = " Did you wrap a component in React.lazy() more than once?";
      throw new Error("Element type is invalid. Received a promise that resolves to: " + P + ". " + ("Lazy element type must resolve to a class or function." + v));
    }
    function V_(Z, X, $, q, H) {
      H5(Z, X), X.tag = F;
      var G;
      if (CX($))
        G = !0, A9(X);
      else
        G = !1;
      return IY(X, H), IL(X, $, q), Hz(X, $, q, H), Oz(null, X, $, !0, G, H);
    }
    function S_(Z, X, $, q) {
      H5(Z, X);
      var H = X.pendingProps, G;
      {
        var E = kY(X, $, !1);
        G = RY(X, E);
      }
      IY(X, q);
      var U, P;
      rq(X);
      {
        if ($.prototype && typeof $.prototype.render === "function") {
          var O = h0($) || "Unknown";
          if (!Ez[O])
            K("The <%s /> component appears to have a render method, but doesn't extend React.Component. This is likely to cause errors. Change %s to extend React.Component instead.", O, O), Ez[O] = !0;
        }
        if (X.mode & j6)
          nZ.recordLegacyContextWarning(X, null);
        dQ(!0), rW.current = X, U = hY(null, X, $, H, G, q), P = yY(), dQ(!1);
      }
      if (HY(), X.flags |= WY, typeof U === "object" && U !== null && typeof U.render === "function" && U.$$typeof === void 0) {
        var k = h0($) || "Unknown";
        if (!iW[k])
          K("The <%s /> component appears to be a function component that returns a class instance. Change %s to a class that extends React.Component instead. If you can't use a class try assigning the prototype on the function as a workaround. `%s.prototype = React.Component.prototype`. Don't use an arrow function since it cannot be called with `new` by React.", k, k, k), iW[k] = !0;
      }
      if (typeof U === "object" && U !== null && typeof U.render === "function" && U.$$typeof === void 0) {
        {
          var C = h0($) || "Unknown";
          if (!iW[C])
            K("The <%s /> component appears to be a function component that returns a class instance. Change %s to a class that extends React.Component instead. If you can't use a class try assigning the prototype on the function as a workaround. `%s.prototype = React.Component.prototype`. Don't use an arrow function since it cannot be called with `new` by React.", C, C, C), iW[C] = !0;
        }
        X.tag = F, X.memoizedState = null, X.updateQueue = null;
        var B = !1;
        if (CX($))
          B = !0, A9(X);
        else
          B = !1;
        return X.memoizedState = U.state !== null && U.state !== void 0 ? U.state : null, A2(X), SL(X, U), Hz(X, $, H, q), Oz(null, X, $, !0, B, q);
      } else {
        if (X.tag = N, X.mode & j6) {
          F8(!0);
          try {
            U = hY(null, X, $, H, G, q), P = yY();
          } finally {
            F8(!1);
          }
        }
        if (S8() && P)
          iG(X);
        return EQ(null, X, U, q), wz(X, $), X.child;
      }
    }
    function wz(Z, X) {
      {
        if (X) {
          if (X.childContextTypes)
            K("%s(...): childContextTypes cannot be defined on a function component.", X.displayName || X.name || "Component");
        }
        if (Z.ref !== null) {
          var $ = "", q = bZ();
          if (q)
            $ += `

Check the render method of \`` + q + "`.";
          var H = q || "", G = Z._debugSource;
          if (G)
            H = G.fileName + ":" + G.lineNumber;
          if (!Pz[H])
            Pz[H] = !0, K("Function components cannot be given refs. Attempts to access this ref will fail. Did you mean to use React.forwardRef()?%s", $);
        }
        if (X.defaultProps !== void 0) {
          var E = h0(X) || "Unknown";
          if (!tW[E])
            K("%s: Support for defaultProps will be removed from function components in a future major release. Use JavaScript default parameters instead.", E), tW[E] = !0;
        }
        if (typeof X.getDerivedStateFromProps === "function") {
          var U = h0(X) || "Unknown";
          if (!Uz[U])
            K("%s: Function components do not support getDerivedStateFromProps.", U), Uz[U] = !0;
        }
        if (typeof X.contextType === "object" && X.contextType !== null) {
          var P = h0(X) || "Unknown";
          if (!Fz[P])
            K("%s: Function components do not support contextType.", P), Fz[P] = !0;
        }
      }
    }
    var Mz = {
      dehydrated: null,
      treeContext: null,
      retryLane: U8
    };
    function Dz(Z) {
      return {
        baseLanes: Z,
        cachePool: O_(),
        transitions: null
      };
    }
    function I_(Z, X) {
      var $ = null;
      return {
        baseLanes: Q1(Z.baseLanes, X),
        cachePool: $,
        transitions: Z.transitions
      };
    }
    function __(Z, X, $, q) {
      if (X !== null) {
        var H = X.memoizedState;
        if (H === null)
          return !1;
      }
      return D2(Z, uW);
    }
    function T_(Z, X) {
      return mK(Z.childLanes, X);
    }
    function dL(Z, X, $) {
      var q = X.pendingProps;
      if (ng(X))
        X.flags |= I1;
      var H = sZ.current, G = !1, E = (X.flags & I1) !== S0;
      if (E || __(H, Z))
        G = !0, X.flags &= ~I1;
      else if (Z === null || Z.memoizedState !== null)
        H = iI(H, iA);
      if (H = TY(H), t4(X, H), Z === null) {
        X2(X);
        var U = X.memoizedState;
        if (U !== null) {
          var P = U.dehydrated;
          if (P !== null)
            return y_(X, P);
        }
        var { children: O, fallback: k } = q;
        if (G) {
          var C = g_(X, O, k, $), B = X.child;
          return B.memoizedState = Dz($), X.memoizedState = Mz, C;
        } else
          return kz(X, O);
      } else {
        var v = Z.memoizedState;
        if (v !== null) {
          var h = v.dehydrated;
          if (h !== null)
            return f_(Z, X, E, q, h, v, $);
        }
        if (G) {
          var { fallback: f, children: q0 } = q, k0 = v_(Z, X, q0, f, $), w0 = X.child, N1 = Z.child.memoizedState;
          return w0.memoizedState = N1 === null ? Dz($) : I_(N1, $), w0.childLanes = T_(Z, $), X.memoizedState = Mz, k0;
        } else {
          var E1 = q.children, _ = x_(Z, X, E1, $);
          return X.memoizedState = null, _;
        }
      }
    }
    function kz(Z, X, $) {
      var q = Z.mode, H = {
        mode: "visible",
        children: X
      }, G = Rz(H, q);
      return G.return = Z, Z.child = G, G;
    }
    function g_(Z, X, $, q) {
      var { mode: H, child: G } = Z, E = {
        mode: "hidden",
        children: X
      }, U, P;
      if ((H & A1) === B0 && G !== null) {
        if (U = G, U.childLanes = n, U.pendingProps = E, Z.mode & b1)
          U.actualDuration = 0, U.actualStartTime = -1, U.selfBaseDuration = 0, U.treeBaseDuration = 0;
        P = qJ($, H, q, null);
      } else
        U = Rz(E, H), P = qJ($, H, q, null);
      return U.return = Z, P.return = Z, U.sibling = P, Z.child = U, P;
    }
    function Rz(Z, X, $) {
      return nO(Z, X, n, null);
    }
    function lL(Z, X) {
      return M$(Z, X);
    }
    function x_(Z, X, $, q) {
      var H = Z.child, G = H.sibling, E = lL(H, {
        mode: "visible",
        children: $
      });
      if ((X.mode & A1) === B0)
        E.lanes = q;
      if (E.return = X, E.sibling = null, G !== null) {
        var U = X.deletions;
        if (U === null)
          X.deletions = [G], X.flags |= sJ;
        else
          U.push(G);
      }
      return X.child = E, E;
    }
    function v_(Z, X, $, q, H) {
      var G = X.mode, E = Z.child, U = E.sibling, P = {
        mode: "hidden",
        children: $
      }, O;
      if ((G & A1) === B0 && X.child !== E) {
        var k = X.child;
        if (O = k, O.childLanes = n, O.pendingProps = P, X.mode & b1)
          O.actualDuration = 0, O.actualStartTime = -1, O.selfBaseDuration = E.selfBaseDuration, O.treeBaseDuration = E.treeBaseDuration;
        X.deletions = null;
      } else
        O = lL(E, P), O.subtreeFlags = E.subtreeFlags & X4;
      var C;
      if (U !== null)
        C = M$(U, q);
      else
        C = qJ(q, G, H, null), C.flags |= m6;
      return C.return = X, O.return = X, O.sibling = C, X.child = O, C;
    }
    function K5(Z, X, $, q) {
      if (q !== null)
        J2(q);
      VY(X, Z.child, null, $);
      var H = X.pendingProps, G = H.children, E = kz(X, G);
      return E.flags |= m6, X.memoizedState = null, E;
    }
    function h_(Z, X, $, q, H) {
      var G = X.mode, E = {
        mode: "visible",
        children: $
      }, U = Rz(E, G), P = qJ(q, G, H, null);
      if (P.flags |= m6, U.return = X, P.return = X, U.sibling = P, X.child = U, (X.mode & A1) !== B0)
        VY(X, Z.child, null, H);
      return P;
    }
    function y_(Z, X, $) {
      if ((Z.mode & A1) === B0)
        K("Cannot hydrate Suspense in legacy mode. Switch from ReactDOM.hydrate(element, container) to ReactDOMClient.hydrateRoot(container, <App />).render(element) or remove the Suspense components from the server rendered components."), Z.lanes = bK(b0);
      else if (cG(X))
        Z.lanes = bK(Q$);
      else
        Z.lanes = bK(lQ);
      return null;
    }
    function f_(Z, X, $, q, H, G, E) {
      if (!$) {
        if (BI(), (X.mode & A1) === B0)
          return K5(Z, X, E, null);
        if (cG(H)) {
          var U, P, O;
          {
            var k = pS(H);
            U = k.digest, P = k.message, O = k.stack;
          }
          var C;
          if (P)
            C = new Error(P);
          else
            C = new Error("The server could not finish this Suspense boundary, likely due to an error during server rendering. Switched to client rendering.");
          var B = Gz(C, U, O);
          return K5(Z, X, E, B);
        }
        var v = nQ(E, Z.childLanes);
        if (rZ || v) {
          var h = O5();
          if (h !== null) {
            var f = aB(h, E);
            if (f !== U8 && f !== G.retryLane) {
              G.retryLane = f;
              var q0 = J6;
              _Q(Z, f), Z8(h, Z, f, q0);
            }
          }
          nz();
          var k0 = Gz(new Error("This Suspense boundary received an update before it finished hydrating. This caused the boundary to switch to client rendering. The usual way to fix this is to wrap the original update in startTransition."));
          return K5(Z, X, E, k0);
        } else if (EA(H)) {
          X.flags |= I1, X.child = Z.child;
          var w0 = Fg.bind(null, Z);
          return dS(H, w0), null;
        } else {
          SI(X, H, G.treeContext);
          var N1 = q.children, E1 = kz(X, N1);
          return E1.flags |= Q4, E1;
        }
      } else if (X.flags & eX) {
        X.flags &= ~eX;
        var _ = Gz(new Error("There was an error while hydrating this Suspense boundary. Switched to client rendering."));
        return K5(Z, X, E, _);
      } else if (X.memoizedState !== null)
        return X.child = Z.child, X.flags |= I1, null;
      else {
        var { children: b, fallback: T } = q, a = h_(Z, X, b, T, E), E0 = X.child;
        return E0.memoizedState = Dz(E), X.memoizedState = Mz, a;
      }
    }
    function nL(Z, X, $) {
      Z.lanes = Q1(Z.lanes, X);
      var q = Z.alternate;
      if (q !== null)
        q.lanes = Q1(q.lanes, X);
      E2(Z.return, X, $);
    }
    function m_(Z, X, $) {
      var q = X;
      while (q !== null) {
        if (q.tag === l) {
          var H = q.memoizedState;
          if (H !== null)
            nL(q, $, Z);
        } else if (q.tag === p)
          nL(q, $, Z);
        else if (q.child !== null) {
          q.child.return = q, q = q.child;
          continue;
        }
        if (q === Z)
          return;
        while (q.sibling === null) {
          if (q.return === null || q.return === Z)
            return;
          q = q.return;
        }
        q.sibling.return = q.return, q = q.sibling;
      }
    }
    function b_(Z) {
      var X = Z, $ = null;
      while (X !== null) {
        var q = X.alternate;
        if (q !== null && f9(q) === null)
          $ = X;
        X = X.sibling;
      }
      return $;
    }
    function u_(Z) {
      if (Z !== void 0 && Z !== "forwards" && Z !== "backwards" && Z !== "together" && !Az[Z])
        if (Az[Z] = !0, typeof Z === "string")
          switch (Z.toLowerCase()) {
            case "together":
            case "forwards":
            case "backwards": {
              K('"%s" is not a valid value for revealOrder on <SuspenseList />. Use lowercase "%s" instead.', Z, Z.toLowerCase());
              break;
            }
            case "forward":
            case "backward": {
              K('"%s" is not a valid value for revealOrder on <SuspenseList />. React uses the -s suffix in the spelling. Use "%ss" instead.', Z, Z.toLowerCase());
              break;
            }
            default:
              K('"%s" is not a supported revealOrder on <SuspenseList />. Did you mean "together", "forwards" or "backwards"?', Z);
              break;
          }
        else
          K('%s is not a supported value for revealOrder on <SuspenseList />. Did you mean "together", "forwards" or "backwards"?', Z);
    }
    function c_(Z, X) {
      if (Z !== void 0 && !W5[Z]) {
        if (Z !== "collapsed" && Z !== "hidden")
          W5[Z] = !0, K('"%s" is not a supported value for tail on <SuspenseList />. Did you mean "collapsed" or "hidden"?', Z);
        else if (X !== "forwards" && X !== "backwards")
          W5[Z] = !0, K('<SuspenseList tail="%s" /> is only valid if revealOrder is "forwards" or "backwards". Did you mean to specify revealOrder="forwards"?', Z);
      }
    }
    function sL(Z, X) {
      {
        var $ = S1(Z), q = !$ && typeof mZ(Z) === "function";
        if ($ || q) {
          var H = $ ? "array" : "iterable";
          return K("A nested %s was passed to row #%s in <SuspenseList />. Wrap it in an additional SuspenseList to configure its revealOrder: <SuspenseList revealOrder=...> ... <SuspenseList revealOrder=...>{%s}</SuspenseList> ... </SuspenseList>", H, X, H), !1;
        }
      }
      return !0;
    }
    function p_(Z, X) {
      if ((X === "forwards" || X === "backwards") && Z !== void 0 && Z !== null && Z !== !1)
        if (S1(Z)) {
          for (var $ = 0;$ < Z.length; $++)
            if (!sL(Z[$], $))
              return;
        } else {
          var q = mZ(Z);
          if (typeof q === "function") {
            var H = q.call(Z);
            if (H) {
              var G = H.next(), E = 0;
              for (;!G.done; G = H.next()) {
                if (!sL(G.value, E))
                  return;
                E++;
              }
            }
          } else
            K('A single row was passed to a <SuspenseList revealOrder="%s" />. This is not useful since it needs multiple rows. Did you mean to pass multiple children or an array?', X);
        }
    }
    function jz(Z, X, $, q, H) {
      var G = Z.memoizedState;
      if (G === null)
        Z.memoizedState = {
          isBackwards: X,
          rendering: null,
          renderingStartTime: 0,
          last: q,
          tail: $,
          tailMode: H
        };
      else
        G.isBackwards = X, G.rendering = null, G.renderingStartTime = 0, G.last = q, G.tail = $, G.tailMode = H;
    }
    function oL(Z, X, $) {
      var q = X.pendingProps, H = q.revealOrder, G = q.tail, E = q.children;
      u_(H), c_(G, H), p_(E, H), EQ(Z, X, E, $);
      var U = sZ.current, P = D2(U, uW);
      if (P)
        U = k2(U, uW), X.flags |= I1;
      else {
        var O = Z !== null && (Z.flags & I1) !== S0;
        if (O)
          m_(X, X.child, $);
        U = TY(U);
      }
      if (t4(X, U), (X.mode & A1) === B0)
        X.memoizedState = null;
      else
        switch (H) {
          case "forwards": {
            var k = b_(X.child), C;
            if (k === null)
              C = X.child, X.child = null;
            else
              C = k.sibling, k.sibling = null;
            jz(X, !1, C, k, G);
            break;
          }
          case "backwards": {
            var B = null, v = X.child;
            X.child = null;
            while (v !== null) {
              var h = v.alternate;
              if (h !== null && f9(h) === null) {
                X.child = v;
                break;
              }
              var f = v.sibling;
              v.sibling = B, B = v, v = f;
            }
            jz(X, !0, B, null, G);
            break;
          }
          case "together": {
            jz(X, !1, null, null, void 0);
            break;
          }
          default:
            X.memoizedState = null;
        }
      return X.child;
    }
    function d_(Z, X, $) {
      O2(X, X.stateNode.containerInfo);
      var q = X.pendingProps;
      if (Z === null)
        X.child = VY(X, null, q, $);
      else
        EQ(Z, X, q, $);
      return X.child;
    }
    var aL = !1;
    function l_(Z, X, $) {
      var q = X.type, H = q._context, G = X.pendingProps, E = X.memoizedProps, U = G.value;
      {
        if (!("value" in G)) {
          if (!aL)
            aL = !0, K("The `value` prop is required for the `<Context.Provider>`. Did you misspell it or forget to pass it?");
        }
        var P = X.type.propTypes;
        if (P)
          dZ(P, G, "prop", "Context.Provider");
      }
      if (uA(X, H, U), E !== null) {
        var O = E.value;
        if (aQ(O, U)) {
          if (E.children === G.children && !U9())
            return N4(Z, X, $);
        } else
          cI(X, H, $);
      }
      var k = G.children;
      return EQ(Z, X, k, $), X.child;
    }
    var rL = !1;
    function n_(Z, X, $) {
      var q = X.type;
      if (q._context === void 0) {
        if (q !== q.Consumer) {
          if (!rL)
            rL = !0, K("Rendering <Context> directly is not supported and will be removed in a future major release. Did you mean to render <Context.Consumer> instead?");
        }
      } else
        q = q._context;
      var H = X.pendingProps, G = H.children;
      if (typeof G !== "function")
        K("A context consumer was rendered with multiple children, or a child that isn't a function. A context consumer expects a single child that is a function. If you did pass a function, make sure there is no trailing or leading whitespace around it.");
      IY(X, $);
      var E = b6(q);
      rq(X);
      var U;
      return rW.current = X, dQ(!0), U = G(E), dQ(!1), HY(), X.flags |= WY, EQ(Z, X, U, $), X.child;
    }
    function eW() {
      rZ = !0;
    }
    function H5(Z, X) {
      if ((X.mode & A1) === B0) {
        if (Z !== null)
          Z.alternate = null, X.alternate = null, X.flags |= m6;
      }
    }
    function N4(Z, X, $) {
      if (Z !== null)
        X.dependencies = Z.dependencies;
      if (jL(), z3(X.lanes), !nQ($, X.childLanes))
        return null;
      return bI(Z, X), X.child;
    }
    function s_(Z, X, $) {
      {
        var q = X.return;
        if (q === null)
          throw new Error("Cannot swap the root fiber.");
        if (Z.alternate = null, X.alternate = null, $.index = X.index, $.sibling = X.sibling, $.return = X.return, $.ref = X.ref, X === q.child)
          q.child = $;
        else {
          var H = q.child;
          if (H === null)
            throw new Error("Expected parent to have a child.");
          while (H.sibling !== X)
            if (H = H.sibling, H === null)
              throw new Error("Expected to find the previous sibling.");
          H.sibling = $;
        }
        var G = q.deletions;
        if (G === null)
          q.deletions = [Z], q.flags |= sJ;
        else
          G.push(Z);
        return $.flags |= m6, $;
      }
    }
    function Bz(Z, X) {
      var $ = Z.lanes;
      if (nQ($, X))
        return !0;
      return !1;
    }
    function o_(Z, X, $) {
      switch (X.tag) {
        case w:
          cL(X);
          var q = X.stateNode;
          CY();
          break;
        case R:
          aA(X);
          break;
        case F: {
          var H = X.type;
          if (CX(H))
            A9(X);
          break;
        }
        case D:
          O2(X, X.stateNode.containerInfo);
          break;
        case F0: {
          var G = X.memoizedProps.value, E = X.type._context;
          uA(X, E, G);
          break;
        }
        case J0:
          {
            var U = nQ($, X.childLanes);
            if (U)
              X.flags |= O1;
            {
              var P = X.stateNode;
              P.effectDuration = 0, P.passiveEffectDuration = 0;
            }
          }
          break;
        case l: {
          var O = X.memoizedState;
          if (O !== null) {
            if (O.dehydrated !== null)
              return t4(X, TY(sZ.current)), X.flags |= I1, null;
            var k = X.child, C = k.childLanes;
            if (nQ($, C))
              return dL(Z, X, $);
            else {
              t4(X, TY(sZ.current));
              var B = N4(Z, X, $);
              if (B !== null)
                return B.sibling;
              else
                return null;
            }
          } else
            t4(X, TY(sZ.current));
          break;
        }
        case p: {
          var v = (Z.flags & I1) !== S0, h = nQ($, X.childLanes);
          if (v) {
            if (h)
              return oL(Z, X, $);
            X.flags |= I1;
          }
          var f = X.memoizedState;
          if (f !== null)
            f.rendering = null, f.tail = null, f.lastEffect = null;
          if (t4(X, sZ.current), h)
            break;
          else
            return null;
        }
        case Y0:
        case A0:
          return X.lanes = n, mL(Z, X, $);
      }
      return N4(Z, X, $);
    }
    function iL(Z, X, $) {
      if (X._debugNeedsRemount && Z !== null)
        return s_(Z, X, JN(X.type, X.key, X.pendingProps, X._debugOwner || null, X.mode, X.lanes));
      if (Z !== null) {
        var q = Z.memoizedProps, H = X.pendingProps;
        if (q !== H || U9() || X.type !== Z.type)
          rZ = !0;
        else {
          var G = Bz(Z, $);
          if (!G && (X.flags & I1) === S0)
            return rZ = !1, o_(Z, X, $);
          if ((Z.flags & _7) !== S0)
            rZ = !0;
          else
            rZ = !1;
        }
      } else if (rZ = !1, S8() && wI(X)) {
        var E = X.index, U = MI();
        jA(X, U, E);
      }
      switch (X.lanes = n, X.tag) {
        case L:
          return S_(Z, X, X.type, $);
        case M0: {
          var P = X.elementType;
          return C_(Z, X, P, $);
        }
        case N: {
          var { type: O, pendingProps: k } = X, C = X.elementType === O ? k : aZ(O, k);
          return Lz(Z, X, O, C, $);
        }
        case F: {
          var { type: B, pendingProps: v } = X, h = X.elementType === B ? v : aZ(B, v);
          return uL(Z, X, B, h, $);
        }
        case w:
          return R_(Z, X, $);
        case R:
          return j_(Z, X, $);
        case V:
          return B_(Z, X);
        case l:
          return dL(Z, X, $);
        case D:
          return d_(Z, X, $);
        case r: {
          var { type: f, pendingProps: q0 } = X, k0 = X.elementType === f ? q0 : aZ(f, q0);
          return hL(Z, X, f, k0, $);
        }
        case g:
          return M_(Z, X, $);
        case s:
          return D_(Z, X, $);
        case J0:
          return k_(Z, X, $);
        case F0:
          return l_(Z, X, $);
        case i:
          return n_(Z, X, $);
        case t: {
          var { type: w0, pendingProps: N1 } = X, E1 = aZ(w0, N1);
          if (X.type !== X.elementType) {
            var _ = w0.propTypes;
            if (_)
              dZ(_, E1, "prop", h0(w0));
          }
          return E1 = aZ(w0.type, E1), yL(Z, X, w0, E1, $);
        }
        case $0:
          return fL(Z, X, X.type, X.pendingProps, $);
        case c0: {
          var { type: b, pendingProps: T } = X, a = X.elementType === b ? T : aZ(b, T);
          return V_(Z, X, b, a, $);
        }
        case p:
          return oL(Z, X, $);
        case o:
          break;
        case Y0:
          return mL(Z, X, $);
      }
      throw new Error("Unknown unit of work tag (" + X.tag + "). This error is likely caused by a bug in React. Please file an issue.");
    }
    function fY(Z) {
      Z.flags |= O1;
    }
    function tL(Z) {
      Z.flags |= f4, Z.flags |= T7;
    }
    var eL, Cz, QO, ZO;
    eL = function(Z, X, $, q) {
      var H = X.child;
      while (H !== null) {
        if (H.tag === R || H.tag === V)
          AS(Z, H.stateNode);
        else if (H.tag === D)
          ;
        else if (H.child !== null) {
          H.child.return = H, H = H.child;
          continue;
        }
        if (H === X)
          return;
        while (H.sibling === null) {
          if (H.return === null || H.return === X)
            return;
          H = H.return;
        }
        H.sibling.return = H.return, H = H.sibling;
      }
    }, Cz = function(Z, X) {}, QO = function(Z, X, $, q, H) {
      var G = Z.memoizedProps;
      if (G === q)
        return;
      var E = X.stateNode, U = w2(), P = OS(E, $, G, q, H, U);
      if (X.updateQueue = P, P)
        fY(X);
    }, ZO = function(Z, X, $, q) {
      if ($ !== q)
        fY(X);
    };
    function Q3(Z, X) {
      if (S8())
        return;
      switch (Z.tailMode) {
        case "hidden": {
          var $ = Z.tail, q = null;
          while ($ !== null) {
            if ($.alternate !== null)
              q = $;
            $ = $.sibling;
          }
          if (q === null)
            Z.tail = null;
          else
            q.sibling = null;
          break;
        }
        case "collapsed": {
          var H = Z.tail, G = null;
          while (H !== null) {
            if (H.alternate !== null)
              G = H;
            H = H.sibling;
          }
          if (G === null)
            if (!X && Z.tail !== null)
              Z.tail.sibling = null;
            else
              Z.tail = null;
          else
            G.sibling = null;
          break;
        }
      }
    }
    function _8(Z) {
      var X = Z.alternate !== null && Z.alternate.child === Z.child, $ = n, q = S0;
      if (!X) {
        if ((Z.mode & b1) !== B0) {
          var { actualDuration: H, selfBaseDuration: G, child: E } = Z;
          while (E !== null)
            $ = Q1($, Q1(E.lanes, E.childLanes)), q |= E.subtreeFlags, q |= E.flags, H += E.actualDuration, G += E.treeBaseDuration, E = E.sibling;
          Z.actualDuration = H, Z.treeBaseDuration = G;
        } else {
          var U = Z.child;
          while (U !== null)
            $ = Q1($, Q1(U.lanes, U.childLanes)), q |= U.subtreeFlags, q |= U.flags, U.return = Z, U = U.sibling;
        }
        Z.subtreeFlags |= q;
      } else {
        if ((Z.mode & b1) !== B0) {
          var { selfBaseDuration: P, child: O } = Z;
          while (O !== null)
            $ = Q1($, Q1(O.lanes, O.childLanes)), q |= O.subtreeFlags & X4, q |= O.flags & X4, P += O.treeBaseDuration, O = O.sibling;
          Z.treeBaseDuration = P;
        } else {
          var k = Z.child;
          while (k !== null)
            $ = Q1($, Q1(k.lanes, k.childLanes)), q |= k.subtreeFlags & X4, q |= k.flags & X4, k.return = Z, k = k.sibling;
        }
        Z.subtreeFlags |= q;
      }
      return Z.childLanes = $, X;
    }
    function a_(Z, X, $) {
      if (xI() && (X.mode & A1) !== B0 && (X.flags & I1) === S0)
        return TA(X), CY(), X.flags |= eX | oq | NQ, !1;
      var q = D9(X);
      if ($ !== null && $.dehydrated !== null)
        if (Z === null) {
          if (!q)
            throw new Error("A dehydrated suspense component was completed without a hydrated node. This is probably a bug in React.");
          if (TI(X), _8(X), (X.mode & b1) !== B0) {
            var H = $ !== null;
            if (H) {
              var G = X.child;
              if (G !== null)
                X.treeBaseDuration -= G.treeBaseDuration;
            }
          }
          return !1;
        } else {
          if (CY(), (X.flags & I1) === S0)
            X.memoizedState = null;
          if (X.flags |= O1, _8(X), (X.mode & b1) !== B0) {
            var E = $ !== null;
            if (E) {
              var U = X.child;
              if (U !== null)
                X.treeBaseDuration -= U.treeBaseDuration;
            }
          }
          return !1;
        }
      else
        return gA(), !0;
    }
    function XO(Z, X, $) {
      var q = X.pendingProps;
      switch (tG(X), X.tag) {
        case L:
        case M0:
        case $0:
        case N:
        case r:
        case g:
        case s:
        case J0:
        case i:
        case t:
          return _8(X), null;
        case F: {
          var H = X.type;
          if (CX(H))
            P9(X);
          return _8(X), null;
        }
        case w: {
          var G = X.stateNode;
          if (_Y(X), oG(X), j2(), G.pendingContext)
            G.context = G.pendingContext, G.pendingContext = null;
          if (Z === null || Z.child === null) {
            var E = D9(X);
            if (E)
              fY(X);
            else if (Z !== null) {
              var U = Z.memoizedState;
              if (!U.isDehydrated || (X.flags & eX) !== S0)
                X.flags |= oJ, gA();
            }
          }
          return Cz(Z, X), _8(X), null;
        }
        case R: {
          M2(X);
          var P = oA(), O = X.type;
          if (Z !== null && X.stateNode != null) {
            if (QO(Z, X, O, q, P), Z.ref !== X.ref)
              tL(X);
          } else {
            if (!q) {
              if (X.stateNode === null)
                throw new Error("We must have new props for new mounts. This error is likely caused by a bug in React. Please file an issue.");
              return _8(X), null;
            }
            var k = w2(), C = D9(X);
            if (C) {
              if (II(X, P, k))
                fY(X);
            } else {
              var B = PS(O, q, P, k, X);
              if (eL(B, X, !1, !1), X.stateNode = B, LS(B, O, q, P))
                fY(X);
            }
            if (X.ref !== null)
              tL(X);
          }
          return _8(X), null;
        }
        case V: {
          var v = q;
          if (Z && X.stateNode != null) {
            var h = Z.memoizedProps;
            ZO(Z, X, h, v);
          } else {
            if (typeof v !== "string") {
              if (X.stateNode === null)
                throw new Error("We must have new props for new mounts. This error is likely caused by a bug in React. Please file an issue.");
            }
            var f = oA(), q0 = w2(), k0 = D9(X);
            if (k0) {
              if (_I(X))
                fY(X);
            } else
              X.stateNode = wS(v, f, q0, X);
          }
          return _8(X), null;
        }
        case l: {
          gY(X);
          var w0 = X.memoizedState;
          if (Z === null || Z.memoizedState !== null && Z.memoizedState.dehydrated !== null) {
            var N1 = a_(Z, X, w0);
            if (!N1)
              if (X.flags & NQ)
                return X;
              else
                return null;
          }
          if ((X.flags & I1) !== S0) {
            if (X.lanes = $, (X.mode & b1) !== B0)
              i2(X);
            return X;
          }
          var E1 = w0 !== null, _ = Z !== null && Z.memoizedState !== null;
          if (E1 !== _) {
            if (E1) {
              var b = X.child;
              if (b.flags |= aJ, (X.mode & A1) !== B0) {
                var T = Z === null && (X.memoizedProps.unstable_avoidThisFallback !== !0 || !g1);
                if (T || D2(sZ.current, iA))
                  Zg();
                else
                  nz();
              }
            }
          }
          var a = X.updateQueue;
          if (a !== null)
            X.flags |= O1;
          if (_8(X), (X.mode & b1) !== B0) {
            if (E1) {
              var E0 = X.child;
              if (E0 !== null)
                X.treeBaseDuration -= E0.treeBaseDuration;
            }
          }
          return null;
        }
        case D:
          if (_Y(X), Cz(Z, X), Z === null)
            EI(X.stateNode.containerInfo);
          return _8(X), null;
        case F0:
          var H0 = X.type._context;
          return N2(H0, X), _8(X), null;
        case c0: {
          var g0 = X.type;
          if (CX(g0))
            P9(X);
          return _8(X), null;
        }
        case p: {
          gY(X);
          var p0 = X.memoizedState;
          if (p0 === null)
            return _8(X), null;
          var c1 = (X.flags & I1) !== S0, R1 = p0.rendering;
          if (R1 === null)
            if (!c1) {
              var S6 = Jg() && (Z === null || (Z.flags & I1) === S0);
              if (!S6) {
                var j1 = X.child;
                while (j1 !== null) {
                  var B6 = f9(j1);
                  if (B6 !== null) {
                    c1 = !0, X.flags |= I1, Q3(p0, !1);
                    var t8 = B6.updateQueue;
                    if (t8 !== null)
                      X.updateQueue = t8, X.flags |= O1;
                    return X.subtreeFlags = S0, uI(X, $), t4(X, k2(sZ.current, uW)), X.child;
                  }
                  j1 = j1.sibling;
                }
              }
              if (p0.tail !== null && E8() > RO())
                X.flags |= I1, c1 = !0, Q3(p0, !1), X.lanes = QP;
            } else
              Q3(p0, !1);
          else {
            if (!c1) {
              var h8 = f9(R1);
              if (h8 !== null) {
                X.flags |= I1, c1 = !0;
                var tQ = h8.updateQueue;
                if (tQ !== null)
                  X.updateQueue = tQ, X.flags |= O1;
                if (Q3(p0, !0), p0.tail === null && p0.tailMode === "hidden" && !R1.alternate && !S8())
                  return _8(X), null;
              } else if (E8() * 2 - p0.renderingStartTime > RO() && $ !== lQ)
                X.flags |= I1, c1 = !0, Q3(p0, !1), X.lanes = QP;
            }
            if (p0.isBackwards)
              R1.sibling = X.child, X.child = R1;
            else {
              var PQ = p0.last;
              if (PQ !== null)
                PQ.sibling = R1;
              else
                X.child = R1;
              p0.last = R1;
            }
          }
          if (p0.tail !== null) {
            var AQ = p0.tail;
            p0.rendering = AQ, p0.tail = AQ.sibling, p0.renderingStartTime = E8(), AQ.sibling = null;
            var e8 = sZ.current;
            if (c1)
              e8 = k2(e8, uW);
            else
              e8 = TY(e8);
            return t4(X, e8), AQ;
          }
          return _8(X), null;
        }
        case o:
          break;
        case Y0:
        case A0: {
          lz(X);
          var A4 = X.memoizedState, nY = A4 !== null;
          if (Z !== null) {
            var P3 = Z.memoizedState, vX = P3 !== null;
            if (vX !== nY && !n1)
              X.flags |= aJ;
          }
          if (!nY || (X.mode & A1) === B0)
            _8(X);
          else if (nQ(xX, lQ)) {
            if (_8(X), X.subtreeFlags & (m6 | O1))
              X.flags |= aJ;
          }
          return null;
        }
        case P0:
          return null;
        case Y1:
          return null;
      }
      throw new Error("Unknown unit of work tag (" + X.tag + "). This error is likely caused by a bug in React. Please file an issue.");
    }
    function r_(Z, X, $) {
      switch (tG(X), X.tag) {
        case F: {
          var q = X.type;
          if (CX(q))
            P9(X);
          var H = X.flags;
          if (H & NQ) {
            if (X.flags = H & ~NQ | I1, (X.mode & b1) !== B0)
              i2(X);
            return X;
          }
          return null;
        }
        case w: {
          var G = X.stateNode;
          _Y(X), oG(X), j2();
          var E = X.flags;
          if ((E & NQ) !== S0 && (E & I1) === S0)
            return X.flags = E & ~NQ | I1, X;
          return null;
        }
        case R:
          return M2(X), null;
        case l: {
          gY(X);
          var U = X.memoizedState;
          if (U !== null && U.dehydrated !== null) {
            if (X.alternate === null)
              throw new Error("Threw in newly mounted dehydrated component. This is likely a bug in React. Please file an issue.");
            CY();
          }
          var P = X.flags;
          if (P & NQ) {
            if (X.flags = P & ~NQ | I1, (X.mode & b1) !== B0)
              i2(X);
            return X;
          }
          return null;
        }
        case p:
          return gY(X), null;
        case D:
          return _Y(X), null;
        case F0:
          var O = X.type._context;
          return N2(O, X), null;
        case Y0:
        case A0:
          return lz(X), null;
        case P0:
          return null;
        default:
          return null;
      }
    }
    function JO(Z, X, $) {
      switch (tG(X), X.tag) {
        case F: {
          var q = X.type.childContextTypes;
          if (q !== null && q !== void 0)
            P9(X);
          break;
        }
        case w: {
          var H = X.stateNode;
          _Y(X), oG(X), j2();
          break;
        }
        case R: {
          M2(X);
          break;
        }
        case D:
          _Y(X);
          break;
        case l:
          gY(X);
          break;
        case p:
          gY(X);
          break;
        case F0:
          var G = X.type._context;
          N2(G, X);
          break;
        case Y0:
        case A0:
          lz(X);
          break;
      }
    }
    var $O = null;
    $O = /* @__PURE__ */ new Set;
    var G5 = !1, T8 = !1, i_ = typeof WeakSet === "function" ? WeakSet : Set, L0 = null, mY = null, bY = null;
    function t_(Z) {
      V7(null, function() {
        throw Z;
      }), S7();
    }
    var e_ = function(Z, X) {
      if (X.props = Z.memoizedProps, X.state = Z.memoizedState, Z.mode & b1)
        try {
          TX(), X.componentWillUnmount();
        } finally {
          _X(Z);
        }
      else
        X.componentWillUnmount();
    };
    function YO(Z, X) {
      try {
        ZJ(a6, Z);
      } catch ($) {
        Z6(Z, X, $);
      }
    }
    function Vz(Z, X, $) {
      try {
        e_(Z, $);
      } catch (q) {
        Z6(Z, X, q);
      }
    }
    function QT(Z, X, $) {
      try {
        $.componentDidMount();
      } catch (q) {
        Z6(Z, X, q);
      }
    }
    function qO(Z, X) {
      try {
        HO(Z);
      } catch ($) {
        Z6(Z, X, $);
      }
    }
    function uY(Z, X) {
      var $ = Z.ref;
      if ($ !== null)
        if (typeof $ === "function") {
          var q;
          try {
            if (N6 && C6 && Z.mode & b1)
              try {
                TX(), q = $(null);
              } finally {
                _X(Z);
              }
            else
              q = $(null);
          } catch (H) {
            Z6(Z, X, H);
          }
          if (typeof q === "function")
            K("Unexpected return value from a callback ref in %s. A callback ref should not return a function.", V0(Z));
        } else
          $.current = null;
    }
    function z5(Z, X, $) {
      try {
        $();
      } catch (q) {
        Z6(Z, X, q);
      }
    }
    var WO = null, KO = !1;
    function ZT(Z, X) {
      WO = FS(Z.containerInfo), L0 = X, XT();
      var $ = KO;
      return KO = !1, WO = null, $;
    }
    function XT() {
      while (L0 !== null) {
        var Z = L0, X = Z.child;
        if ((Z.subtreeFlags & x7) !== S0 && X !== null)
          X.return = Z, L0 = X;
        else
          JT();
      }
    }
    function JT() {
      while (L0 !== null) {
        var Z = L0;
        w6(Z);
        try {
          $T(Z);
        } catch ($) {
          Z6(Z, Z.return, $);
        }
        N8();
        var X = Z.sibling;
        if (X !== null) {
          X.return = Z.return, L0 = X;
          return;
        }
        L0 = Z.return;
      }
    }
    function $T(Z) {
      var { alternate: X, flags: $ } = Z;
      if (($ & oJ) !== S0) {
        switch (w6(Z), Z.tag) {
          case N:
          case r:
          case $0:
            break;
          case F: {
            if (X !== null) {
              var { memoizedProps: q, memoizedState: H } = X, G = Z.stateNode;
              if (Z.type === Z.elementType && !P$) {
                if (G.props !== Z.memoizedProps)
                  K("Expected %s props to match memoized props before getSnapshotBeforeUpdate. This might either be because of a bug in React, or because a component reassigns its own `this.props`. Please file an issue.", V0(Z) || "instance");
                if (G.state !== Z.memoizedState)
                  K("Expected %s state to match memoized state before getSnapshotBeforeUpdate. This might either be because of a bug in React, or because a component reassigns its own `this.state`. Please file an issue.", V0(Z) || "instance");
              }
              var E = G.getSnapshotBeforeUpdate(Z.elementType === Z.type ? q : aZ(Z.type, q), H);
              {
                var U = $O;
                if (E === void 0 && !U.has(Z.type))
                  U.add(Z.type), K("%s.getSnapshotBeforeUpdate(): A snapshot value (or null) must be returned. You have returned undefined.", V0(Z));
              }
              G.__reactInternalSnapshotBeforeUpdate = E;
            }
            break;
          }
          case w: {
            {
              var P = Z.stateNode;
              mS(P.containerInfo);
            }
            break;
          }
          case R:
          case V:
          case D:
          case c0:
            break;
          default:
            throw new Error("This unit of work tag should not have side-effects. This error is likely caused by a bug in React. Please file an issue.");
        }
        N8();
      }
    }
    function iZ(Z, X, $) {
      var q = X.updateQueue, H = q !== null ? q.lastEffect : null;
      if (H !== null) {
        var G = H.next, E = G;
        do {
          if ((E.tag & Z) === Z) {
            var U = E.destroy;
            if (E.destroy = void 0, U !== void 0) {
              if ((Z & I8) !== TQ)
                wB(X);
              else if ((Z & a6) !== TQ)
                aU(X);
              if ((Z & VX) !== TQ)
                E3(!0);
              if (z5(X, $, U), (Z & VX) !== TQ)
                E3(!1);
              if ((Z & I8) !== TQ)
                MB();
              else if ((Z & a6) !== TQ)
                rU();
            }
          }
          E = E.next;
        } while (E !== G);
      }
    }
    function ZJ(Z, X) {
      var $ = X.updateQueue, q = $ !== null ? $.lastEffect : null;
      if (q !== null) {
        var H = q.next, G = H;
        do {
          if ((G.tag & Z) === Z) {
            if ((Z & I8) !== TQ)
              LB(X);
            else if ((Z & a6) !== TQ)
              DB(X);
            var E = G.create;
            if ((Z & VX) !== TQ)
              E3(!0);
            if (G.destroy = E(), (Z & VX) !== TQ)
              E3(!1);
            if ((Z & I8) !== TQ)
              OB();
            else if ((Z & a6) !== TQ)
              kB();
            {
              var U = G.destroy;
              if (U !== void 0 && typeof U !== "function") {
                var P = void 0;
                if ((G.tag & a6) !== S0)
                  P = "useLayoutEffect";
                else if ((G.tag & VX) !== S0)
                  P = "useInsertionEffect";
                else
                  P = "useEffect";
                var O = void 0;
                if (U === null)
                  O = " You returned null. If your effect does not require clean up, return undefined (or nothing).";
                else if (typeof U.then === "function")
                  O = `

It looks like you wrote ` + P + `(async () => ...) or returned a Promise. Instead, write the async function inside your effect and call it immediately:

` + P + `(() => {
  async function fetchData() {
    // You can await here
    const response = await MyAPI.getData(someId);
    // ...
  }
  fetchData();
}, [someId]); // Or [] if effect doesn't need props or state

Learn more about data fetching with Hooks: https://reactjs.org/link/hooks-data-fetching`;
                else
                  O = " You returned: " + U;
                K("%s must not return anything besides a function, which is used for clean-up.%s", P, O);
              }
            }
          }
          G = G.next;
        } while (G !== H);
      }
    }
    function YT(Z, X) {
      if ((X.flags & O1) !== S0)
        switch (X.tag) {
          case J0: {
            var $ = X.stateNode.passiveEffectDuration, q = X.memoizedProps, H = q.id, G = q.onPostCommit, E = kL(), U = X.alternate === null ? "mount" : "update";
            if (DL())
              U = "nested-update";
            if (typeof G === "function")
              G(H, U, $, E);
            var P = X.return;
            Q:
              while (P !== null) {
                switch (P.tag) {
                  case w:
                    var O = P.stateNode;
                    O.passiveEffectDuration += $;
                    break Q;
                  case J0:
                    var k = P.stateNode;
                    k.passiveEffectDuration += $;
                    break Q;
                }
                P = P.return;
              }
            break;
          }
        }
    }
    function qT(Z, X, $, q) {
      if (($.flags & aq) !== S0)
        switch ($.tag) {
          case N:
          case r:
          case $0: {
            if (!T8)
              if ($.mode & b1)
                try {
                  TX(), ZJ(a6 | o6, $);
                } finally {
                  _X($);
                }
              else
                ZJ(a6 | o6, $);
            break;
          }
          case F: {
            var H = $.stateNode;
            if ($.flags & O1) {
              if (!T8)
                if (X === null) {
                  if ($.type === $.elementType && !P$) {
                    if (H.props !== $.memoizedProps)
                      K("Expected %s props to match memoized props before componentDidMount. This might either be because of a bug in React, or because a component reassigns its own `this.props`. Please file an issue.", V0($) || "instance");
                    if (H.state !== $.memoizedState)
                      K("Expected %s state to match memoized state before componentDidMount. This might either be because of a bug in React, or because a component reassigns its own `this.state`. Please file an issue.", V0($) || "instance");
                  }
                  if ($.mode & b1)
                    try {
                      TX(), H.componentDidMount();
                    } finally {
                      _X($);
                    }
                  else
                    H.componentDidMount();
                } else {
                  var G = $.elementType === $.type ? X.memoizedProps : aZ($.type, X.memoizedProps), E = X.memoizedState;
                  if ($.type === $.elementType && !P$) {
                    if (H.props !== $.memoizedProps)
                      K("Expected %s props to match memoized props before componentDidUpdate. This might either be because of a bug in React, or because a component reassigns its own `this.props`. Please file an issue.", V0($) || "instance");
                    if (H.state !== $.memoizedState)
                      K("Expected %s state to match memoized state before componentDidUpdate. This might either be because of a bug in React, or because a component reassigns its own `this.state`. Please file an issue.", V0($) || "instance");
                  }
                  if ($.mode & b1)
                    try {
                      TX(), H.componentDidUpdate(G, E, H.__reactInternalSnapshotBeforeUpdate);
                    } finally {
                      _X($);
                    }
                  else
                    H.componentDidUpdate(G, E, H.__reactInternalSnapshotBeforeUpdate);
                }
            }
            var U = $.updateQueue;
            if (U !== null) {
              if ($.type === $.elementType && !P$) {
                if (H.props !== $.memoizedProps)
                  K("Expected %s props to match memoized props before processing the update queue. This might either be because of a bug in React, or because a component reassigns its own `this.props`. Please file an issue.", V0($) || "instance");
                if (H.state !== $.memoizedState)
                  K("Expected %s state to match memoized state before processing the update queue. This might either be because of a bug in React, or because a component reassigns its own `this.state`. Please file an issue.", V0($) || "instance");
              }
              sA($, U, H);
            }
            break;
          }
          case w: {
            var P = $.updateQueue;
            if (P !== null) {
              var O = null;
              if ($.child !== null)
                switch ($.child.tag) {
                  case R:
                    O = yG($.child.stateNode);
                    break;
                  case F:
                    O = $.child.stateNode;
                    break;
                }
              sA($, P, O);
            }
            break;
          }
          case R: {
            var k = $.stateNode;
            if (X === null && $.flags & O1) {
              var { type: C, memoizedProps: B } = $;
              jS(k, C, B);
            }
            break;
          }
          case V:
            break;
          case D:
            break;
          case J0: {
            {
              var v = $.memoizedProps, h = v.onCommit, f = v.onRender, q0 = $.stateNode.effectDuration, k0 = kL(), w0 = X === null ? "mount" : "update";
              if (DL())
                w0 = "nested-update";
              if (typeof f === "function")
                f($.memoizedProps.id, w0, $.actualDuration, $.treeBaseDuration, $.actualStartTime, k0);
              {
                if (typeof h === "function")
                  h($.memoizedProps.id, w0, q0, k0);
                Kg($);
                var N1 = $.return;
                Q:
                  while (N1 !== null) {
                    switch (N1.tag) {
                      case w:
                        var E1 = N1.stateNode;
                        E1.effectDuration += q0;
                        break Q;
                      case J0:
                        var _ = N1.stateNode;
                        _.effectDuration += q0;
                        break Q;
                    }
                    N1 = N1.return;
                  }
              }
            }
            break;
          }
          case l: {
            FT(Z, $);
            break;
          }
          case p:
          case c0:
          case o:
          case Y0:
          case A0:
          case Y1:
            break;
          default:
            throw new Error("This unit of work tag should not have side-effects. This error is likely caused by a bug in React. Please file an issue.");
        }
      if (!T8) {
        if ($.flags & f4)
          HO($);
      }
    }
    function WT(Z) {
      switch (Z.tag) {
        case N:
        case r:
        case $0: {
          if (Z.mode & b1)
            try {
              TX(), YO(Z, Z.return);
            } finally {
              _X(Z);
            }
          else
            YO(Z, Z.return);
          break;
        }
        case F: {
          var X = Z.stateNode;
          if (typeof X.componentDidMount === "function")
            QT(Z, Z.return, X);
          qO(Z, Z.return);
          break;
        }
        case R: {
          qO(Z, Z.return);
          break;
        }
      }
    }
    function KT(Z, X) {
      var $ = null;
      {
        var q = Z;
        while (!0) {
          if (q.tag === R) {
            if ($ === null) {
              $ = q;
              try {
                var H = q.stateNode;
                if (X)
                  vS(H);
                else
                  yS(q.stateNode, q.memoizedProps);
              } catch (E) {
                Z6(Z, Z.return, E);
              }
            }
          } else if (q.tag === V) {
            if ($ === null)
              try {
                var G = q.stateNode;
                if (X)
                  hS(G);
                else
                  fS(G, q.memoizedProps);
              } catch (E) {
                Z6(Z, Z.return, E);
              }
          } else if ((q.tag === Y0 || q.tag === A0) && q.memoizedState !== null && q !== Z)
            ;
          else if (q.child !== null) {
            q.child.return = q, q = q.child;
            continue;
          }
          if (q === Z)
            return;
          while (q.sibling === null) {
            if (q.return === null || q.return === Z)
              return;
            if ($ === q)
              $ = null;
            q = q.return;
          }
          if ($ === q)
            $ = null;
          q.sibling.return = q.return, q = q.sibling;
        }
      }
    }
    function HO(Z) {
      var X = Z.ref;
      if (X !== null) {
        var $ = Z.stateNode, q;
        switch (Z.tag) {
          case R:
            q = yG($);
            break;
          default:
            q = $;
        }
        if (typeof X === "function") {
          var H;
          if (Z.mode & b1)
            try {
              TX(), H = X(q);
            } finally {
              _X(Z);
            }
          else
            H = X(q);
          if (typeof H === "function")
            K("Unexpected return value from a callback ref in %s. A callback ref should not return a function.", V0(Z));
        } else {
          if (!X.hasOwnProperty("current"))
            K("Unexpected ref object provided for %s. Use either a ref-setter function or React.createRef().", V0(Z));
          X.current = q;
        }
      }
    }
    function HT(Z) {
      var X = Z.alternate;
      if (X !== null)
        X.return = null;
      Z.return = null;
    }
    function GO(Z) {
      var X = Z.alternate;
      if (X !== null)
        Z.alternate = null, GO(X);
      {
        if (Z.child = null, Z.deletions = null, Z.sibling = null, Z.tag === R) {
          var $ = Z.stateNode;
          if ($ !== null)
            PI($);
        }
        Z.stateNode = null, Z._debugOwner = null, Z.return = null, Z.dependencies = null, Z.memoizedProps = null, Z.memoizedState = null, Z.pendingProps = null, Z.stateNode = null, Z.updateQueue = null;
      }
    }
    function GT(Z) {
      var X = Z.return;
      while (X !== null) {
        if (zO(X))
          return X;
        X = X.return;
      }
      throw new Error("Expected to find a host parent. This error is likely caused by a bug in React. Please file an issue.");
    }
    function zO(Z) {
      return Z.tag === R || Z.tag === w || Z.tag === D;
    }
    function NO(Z) {
      var X = Z;
      Q:
        while (!0) {
          while (X.sibling === null) {
            if (X.return === null || zO(X.return))
              return null;
            X = X.return;
          }
          X.sibling.return = X.return, X = X.sibling;
          while (X.tag !== R && X.tag !== V && X.tag !== I0) {
            if (X.flags & m6)
              continue Q;
            if (X.child === null || X.tag === D)
              continue Q;
            else
              X.child.return = X, X = X.child;
          }
          if (!(X.flags & m6))
            return X.stateNode;
        }
    }
    function zT(Z) {
      var X = GT(Z);
      switch (X.tag) {
        case R: {
          var $ = X.stateNode;
          if (X.flags & sq)
            NA($), X.flags &= ~sq;
          var q = NO(Z);
          Iz(Z, q, $);
          break;
        }
        case w:
        case D: {
          var H = X.stateNode.containerInfo, G = NO(Z);
          Sz(Z, G, H);
          break;
        }
        default:
          throw new Error("Invalid host parent fiber. This error is likely caused by a bug in React. Please file an issue.");
      }
    }
    function Sz(Z, X, $) {
      var q = Z.tag, H = q === R || q === V;
      if (H) {
        var G = Z.stateNode;
        if (X)
          _S($, G, X);
        else
          SS($, G);
      } else if (q === D)
        ;
      else {
        var E = Z.child;
        if (E !== null) {
          Sz(E, X, $);
          var U = E.sibling;
          while (U !== null)
            Sz(U, X, $), U = U.sibling;
        }
      }
    }
    function Iz(Z, X, $) {
      var q = Z.tag, H = q === R || q === V;
      if (H) {
        var G = Z.stateNode;
        if (X)
          IS($, G, X);
        else
          VS($, G);
      } else if (q === D)
        ;
      else {
        var E = Z.child;
        if (E !== null) {
          Iz(E, X, $);
          var U = E.sibling;
          while (U !== null)
            Iz(U, X, $), U = U.sibling;
        }
      }
    }
    var g8 = null, tZ = !1;
    function NT(Z, X, $) {
      {
        var q = X;
        Q:
          while (q !== null) {
            switch (q.tag) {
              case R: {
                g8 = q.stateNode, tZ = !1;
                break Q;
              }
              case w: {
                g8 = q.stateNode.containerInfo, tZ = !0;
                break Q;
              }
              case D: {
                g8 = q.stateNode.containerInfo, tZ = !0;
                break Q;
              }
            }
            q = q.return;
          }
        if (g8 === null)
          throw new Error("Expected to find a host parent. This error is likely caused by a bug in React. Please file an issue.");
        EO(Z, X, $), g8 = null, tZ = !1;
      }
      HT($);
    }
    function XJ(Z, X, $) {
      var q = $.child;
      while (q !== null)
        EO(Z, X, q), q = q.sibling;
    }
    function EO(Z, X, $) {
      switch (FB($), $.tag) {
        case R:
          if (!T8)
            uY($, X);
        case V: {
          {
            var q = g8, H = tZ;
            if (g8 = null, XJ(Z, X, $), g8 = q, tZ = H, g8 !== null)
              if (tZ)
                gS(g8, $.stateNode);
              else
                TS(g8, $.stateNode);
          }
          return;
        }
        case I0: {
          if (g8 !== null)
            if (tZ)
              xS(g8, $.stateNode);
            else
              uG(g8, $.stateNode);
          return;
        }
        case D: {
          {
            var G = g8, E = tZ;
            g8 = $.stateNode.containerInfo, tZ = !0, XJ(Z, X, $), g8 = G, tZ = E;
          }
          return;
        }
        case N:
        case r:
        case t:
        case $0: {
          if (!T8) {
            var U = $.updateQueue;
            if (U !== null) {
              var P = U.lastEffect;
              if (P !== null) {
                var O = P.next, k = O;
                do {
                  var C = k, B = C.destroy, v = C.tag;
                  if (B !== void 0) {
                    if ((v & VX) !== TQ)
                      z5($, X, B);
                    else if ((v & a6) !== TQ) {
                      if (aU($), $.mode & b1)
                        TX(), z5($, X, B), _X($);
                      else
                        z5($, X, B);
                      rU();
                    }
                  }
                  k = k.next;
                } while (k !== O);
              }
            }
          }
          XJ(Z, X, $);
          return;
        }
        case F: {
          if (!T8) {
            uY($, X);
            var h = $.stateNode;
            if (typeof h.componentWillUnmount === "function")
              Vz($, X, h);
          }
          XJ(Z, X, $);
          return;
        }
        case o: {
          XJ(Z, X, $);
          return;
        }
        case Y0: {
          if ($.mode & A1) {
            var f = T8;
            T8 = f || $.memoizedState !== null, XJ(Z, X, $), T8 = f;
          } else
            XJ(Z, X, $);
          break;
        }
        default: {
          XJ(Z, X, $);
          return;
        }
      }
    }
    function ET(Z) {
      var X = Z.memoizedState;
    }
    function FT(Z, X) {
      var $ = X.memoizedState;
      if ($ === null) {
        var q = X.alternate;
        if (q !== null) {
          var H = q.memoizedState;
          if (H !== null) {
            var G = H.dehydrated;
            if (G !== null)
              eS(G);
          }
        }
      }
    }
    function FO(Z) {
      var X = Z.updateQueue;
      if (X !== null) {
        Z.updateQueue = null;
        var $ = Z.stateNode;
        if ($ === null)
          $ = Z.stateNode = new i_;
        X.forEach(function(q) {
          var H = Ug.bind(null, Z, q);
          if (!$.has(q)) {
            if ($.add(q), cZ)
              if (mY !== null && bY !== null)
                N3(bY, mY);
              else
                throw Error("Expected finished root and lanes to be set. This is a bug in React.");
            q.then(H, H);
          }
        });
      }
    }
    function UT(Z, X, $) {
      mY = $, bY = Z, w6(X), UO(X, Z), w6(X), mY = null, bY = null;
    }
    function eZ(Z, X, $) {
      var q = X.deletions;
      if (q !== null)
        for (var H = 0;H < q.length; H++) {
          var G = q[H];
          try {
            NT(Z, X, G);
          } catch (P) {
            Z6(G, X, P);
          }
        }
      var E = LK();
      if (X.subtreeFlags & v7) {
        var U = X.child;
        while (U !== null)
          w6(U), UO(U, Z), U = U.sibling;
      }
      w6(E);
    }
    function UO(Z, X, $) {
      var { alternate: q, flags: H } = Z;
      switch (Z.tag) {
        case N:
        case r:
        case t:
        case $0: {
          if (eZ(X, Z), gX(Z), H & O1) {
            try {
              iZ(VX | o6, Z, Z.return), ZJ(VX | o6, Z);
            } catch (g0) {
              Z6(Z, Z.return, g0);
            }
            if (Z.mode & b1) {
              try {
                TX(), iZ(a6 | o6, Z, Z.return);
              } catch (g0) {
                Z6(Z, Z.return, g0);
              }
              _X(Z);
            } else
              try {
                iZ(a6 | o6, Z, Z.return);
              } catch (g0) {
                Z6(Z, Z.return, g0);
              }
          }
          return;
        }
        case F: {
          if (eZ(X, Z), gX(Z), H & f4) {
            if (q !== null)
              uY(q, q.return);
          }
          return;
        }
        case R: {
          if (eZ(X, Z), gX(Z), H & f4) {
            if (q !== null)
              uY(q, q.return);
          }
          {
            if (Z.flags & sq) {
              var G = Z.stateNode;
              try {
                NA(G);
              } catch (g0) {
                Z6(Z, Z.return, g0);
              }
            }
            if (H & O1) {
              var E = Z.stateNode;
              if (E != null) {
                var U = Z.memoizedProps, P = q !== null ? q.memoizedProps : U, O = Z.type, k = Z.updateQueue;
                if (Z.updateQueue = null, k !== null)
                  try {
                    BS(E, k, O, P, U, Z);
                  } catch (g0) {
                    Z6(Z, Z.return, g0);
                  }
              }
            }
          }
          return;
        }
        case V: {
          if (eZ(X, Z), gX(Z), H & O1) {
            if (Z.stateNode === null)
              throw new Error("This should have a text node initialized. This error is likely caused by a bug in React. Please file an issue.");
            var { stateNode: C, memoizedProps: B } = Z, v = q !== null ? q.memoizedProps : B;
            try {
              CS(C, v, B);
            } catch (g0) {
              Z6(Z, Z.return, g0);
            }
          }
          return;
        }
        case w: {
          if (eZ(X, Z), gX(Z), H & O1) {
            if (q !== null) {
              var h = q.memoizedState;
              if (h.isDehydrated)
                try {
                  tS(X.containerInfo);
                } catch (g0) {
                  Z6(Z, Z.return, g0);
                }
            }
          }
          return;
        }
        case D: {
          eZ(X, Z), gX(Z);
          return;
        }
        case l: {
          eZ(X, Z), gX(Z);
          var f = Z.child;
          if (f.flags & aJ) {
            var { stateNode: q0, memoizedState: k0 } = f, w0 = k0 !== null;
            if (q0.isHidden = w0, w0) {
              var N1 = f.alternate !== null && f.alternate.memoizedState !== null;
              if (!N1)
                Qg();
            }
          }
          if (H & O1) {
            try {
              ET(Z);
            } catch (g0) {
              Z6(Z, Z.return, g0);
            }
            FO(Z);
          }
          return;
        }
        case Y0: {
          var E1 = q !== null && q.memoizedState !== null;
          if (Z.mode & A1) {
            var _ = T8;
            T8 = _ || E1, eZ(X, Z), T8 = _;
          } else
            eZ(X, Z);
          if (gX(Z), H & aJ) {
            var { stateNode: b, memoizedState: T } = Z, a = T !== null, E0 = Z;
            if (b.isHidden = a, a) {
              if (!E1) {
                if ((E0.mode & A1) !== B0) {
                  L0 = E0;
                  var H0 = E0.child;
                  while (H0 !== null)
                    L0 = H0, AT(H0), H0 = H0.sibling;
                }
              }
            }
            KT(E0, a);
          }
          return;
        }
        case p: {
          if (eZ(X, Z), gX(Z), H & O1)
            FO(Z);
          return;
        }
        case o:
          return;
        default: {
          eZ(X, Z), gX(Z);
          return;
        }
      }
    }
    function gX(Z) {
      var X = Z.flags;
      if (X & m6) {
        try {
          zT(Z);
        } catch ($) {
          Z6(Z, Z.return, $);
        }
        Z.flags &= ~m6;
      }
      if (X & Q4)
        Z.flags &= ~Q4;
    }
    function PT(Z, X, $) {
      mY = $, bY = X, L0 = Z, PO(Z, X, $), mY = null, bY = null;
    }
    function PO(Z, X, $) {
      var q = (Z.mode & A1) !== B0;
      while (L0 !== null) {
        var H = L0, G = H.child;
        if (H.tag === Y0 && q) {
          var E = H.memoizedState !== null, U = E || G5;
          if (U) {
            _z(Z, X, $);
            continue;
          } else {
            var P = H.alternate, O = P !== null && P.memoizedState !== null, k = O || T8, C = G5, B = T8;
            if (G5 = U, T8 = k, T8 && !B)
              L0 = H, LT(H);
            var v = G;
            while (v !== null)
              L0 = v, PO(v, X, $), v = v.sibling;
            L0 = H, G5 = C, T8 = B, _z(Z, X, $);
            continue;
          }
        }
        if ((H.subtreeFlags & aq) !== S0 && G !== null)
          G.return = H, L0 = G;
        else
          _z(Z, X, $);
      }
    }
    function _z(Z, X, $) {
      while (L0 !== null) {
        var q = L0;
        if ((q.flags & aq) !== S0) {
          var H = q.alternate;
          w6(q);
          try {
            qT(X, H, q, $);
          } catch (E) {
            Z6(q, q.return, E);
          }
          N8();
        }
        if (q === Z) {
          L0 = null;
          return;
        }
        var G = q.sibling;
        if (G !== null) {
          G.return = q.return, L0 = G;
          return;
        }
        L0 = q.return;
      }
    }
    function AT(Z) {
      while (L0 !== null) {
        var X = L0, $ = X.child;
        switch (X.tag) {
          case N:
          case r:
          case t:
          case $0: {
            if (X.mode & b1)
              try {
                TX(), iZ(a6, X, X.return);
              } finally {
                _X(X);
              }
            else
              iZ(a6, X, X.return);
            break;
          }
          case F: {
            uY(X, X.return);
            var q = X.stateNode;
            if (typeof q.componentWillUnmount === "function")
              Vz(X, X.return, q);
            break;
          }
          case R: {
            uY(X, X.return);
            break;
          }
          case Y0: {
            var H = X.memoizedState !== null;
            if (H) {
              AO(Z);
              continue;
            }
            break;
          }
        }
        if ($ !== null)
          $.return = X, L0 = $;
        else
          AO(Z);
      }
    }
    function AO(Z) {
      while (L0 !== null) {
        var X = L0;
        if (X === Z) {
          L0 = null;
          return;
        }
        var $ = X.sibling;
        if ($ !== null) {
          $.return = X.return, L0 = $;
          return;
        }
        L0 = X.return;
      }
    }
    function LT(Z) {
      while (L0 !== null) {
        var X = L0, $ = X.child;
        if (X.tag === Y0) {
          var q = X.memoizedState !== null;
          if (q) {
            LO(Z);
            continue;
          }
        }
        if ($ !== null)
          $.return = X, L0 = $;
        else
          LO(Z);
      }
    }
    function LO(Z) {
      while (L0 !== null) {
        var X = L0;
        w6(X);
        try {
          WT(X);
        } catch (q) {
          Z6(X, X.return, q);
        }
        if (N8(), X === Z) {
          L0 = null;
          return;
        }
        var $ = X.sibling;
        if ($ !== null) {
          $.return = X.return, L0 = $;
          return;
        }
        L0 = X.return;
      }
    }
    function OT(Z, X, $, q) {
      L0 = X, wT(X, Z, $, q);
    }
    function wT(Z, X, $, q) {
      while (L0 !== null) {
        var H = L0, G = H.child;
        if ((H.subtreeFlags & KY) !== S0 && G !== null)
          G.return = H, L0 = G;
        else
          MT(Z, X, $, q);
      }
    }
    function MT(Z, X, $, q) {
      while (L0 !== null) {
        var H = L0;
        if ((H.flags & uZ) !== S0) {
          w6(H);
          try {
            DT(X, H, $, q);
          } catch (E) {
            Z6(H, H.return, E);
          }
          N8();
        }
        if (H === Z) {
          L0 = null;
          return;
        }
        var G = H.sibling;
        if (G !== null) {
          G.return = H.return, L0 = G;
          return;
        }
        L0 = H.return;
      }
    }
    function DT(Z, X, $, q) {
      switch (X.tag) {
        case N:
        case r:
        case $0: {
          if (X.mode & b1) {
            r2();
            try {
              ZJ(I8 | o6, X);
            } finally {
              a2(X);
            }
          } else
            ZJ(I8 | o6, X);
          break;
        }
      }
    }
    function kT(Z) {
      L0 = Z, RT();
    }
    function RT() {
      while (L0 !== null) {
        var Z = L0, X = Z.child;
        if ((L0.flags & sJ) !== S0) {
          var $ = Z.deletions;
          if ($ !== null) {
            for (var q = 0;q < $.length; q++) {
              var H = $[q];
              L0 = H, CT(H, Z);
            }
            {
              var G = Z.alternate;
              if (G !== null) {
                var E = G.child;
                if (E !== null) {
                  G.child = null;
                  do {
                    var U = E.sibling;
                    E.sibling = null, E = U;
                  } while (E !== null);
                }
              }
            }
            L0 = Z;
          }
        }
        if ((Z.subtreeFlags & KY) !== S0 && X !== null)
          X.return = Z, L0 = X;
        else
          jT();
      }
    }
    function jT() {
      while (L0 !== null) {
        var Z = L0;
        if ((Z.flags & uZ) !== S0)
          w6(Z), BT(Z), N8();
        var X = Z.sibling;
        if (X !== null) {
          X.return = Z.return, L0 = X;
          return;
        }
        L0 = Z.return;
      }
    }
    function BT(Z) {
      switch (Z.tag) {
        case N:
        case r:
        case $0: {
          if (Z.mode & b1)
            r2(), iZ(I8 | o6, Z, Z.return), a2(Z);
          else
            iZ(I8 | o6, Z, Z.return);
          break;
        }
      }
    }
    function CT(Z, X) {
      while (L0 !== null) {
        var $ = L0;
        w6($), ST($, X), N8();
        var q = $.child;
        if (q !== null)
          q.return = $, L0 = q;
        else
          VT(Z);
      }
    }
    function VT(Z) {
      while (L0 !== null) {
        var X = L0, $ = X.sibling, q = X.return;
        if (GO(X), X === Z) {
          L0 = null;
          return;
        }
        if ($ !== null) {
          $.return = q, L0 = $;
          return;
        }
        L0 = q;
      }
    }
    function ST(Z, X) {
      switch (Z.tag) {
        case N:
        case r:
        case $0: {
          if (Z.mode & b1)
            r2(), iZ(I8, Z, X), a2(Z);
          else
            iZ(I8, Z, X);
          break;
        }
      }
    }
    function IT(Z) {
      switch (Z.tag) {
        case N:
        case r:
        case $0: {
          try {
            ZJ(a6 | o6, Z);
          } catch ($) {
            Z6(Z, Z.return, $);
          }
          break;
        }
        case F: {
          var X = Z.stateNode;
          try {
            X.componentDidMount();
          } catch ($) {
            Z6(Z, Z.return, $);
          }
          break;
        }
      }
    }
    function _T(Z) {
      switch (Z.tag) {
        case N:
        case r:
        case $0: {
          try {
            ZJ(I8 | o6, Z);
          } catch (X) {
            Z6(Z, Z.return, X);
          }
          break;
        }
      }
    }
    function TT(Z) {
      switch (Z.tag) {
        case N:
        case r:
        case $0: {
          try {
            iZ(a6 | o6, Z, Z.return);
          } catch ($) {
            Z6(Z, Z.return, $);
          }
          break;
        }
        case F: {
          var X = Z.stateNode;
          if (typeof X.componentWillUnmount === "function")
            Vz(Z, Z.return, X);
          break;
        }
      }
    }
    function gT(Z) {
      switch (Z.tag) {
        case N:
        case r:
        case $0:
          try {
            iZ(I8 | o6, Z, Z.return);
          } catch (X) {
            Z6(Z, Z.return, X);
          }
      }
    }
    var xT = 0, vT = 1, hT = 2, yT = 3, fT = 4;
    if (typeof Symbol === "function" && Symbol.for) {
      var Z3 = Symbol.for;
      xT = Z3("selector.component"), vT = Z3("selector.has_pseudo_class"), hT = Z3("selector.role"), yT = Z3("selector.test_id"), fT = Z3("selector.text");
    }
    var mT = [];
    function bT() {
      mT.forEach(function(Z) {
        return Z();
      });
    }
    var uT = Q.ReactCurrentActQueue;
    function cT(Z) {
      {
        var X = typeof IS_REACT_ACT_ENVIRONMENT !== "undefined" ? IS_REACT_ACT_ENVIRONMENT : void 0, $ = typeof jest !== "undefined";
        return $ && X !== !1;
      }
    }
    function OO() {
      {
        var Z = typeof IS_REACT_ACT_ENVIRONMENT !== "undefined" ? IS_REACT_ACT_ENVIRONMENT : void 0;
        if (!Z && uT.current !== null)
          K("The current testing environment is not configured to support act(...)");
        return Z;
      }
    }
    var pT = Math.ceil, Tz = Q.ReactCurrentDispatcher, gz = Q.ReactCurrentOwner, x8 = Q.ReactCurrentBatchConfig, QX = Q.ReactCurrentActQueue, t6 = 0, wO = 1, v8 = 2, UZ = 4, E4 = 0, X3 = 1, A$ = 2, N5 = 3, J3 = 4, MO = 5, xz = 6, L1 = t6, FQ = null, M6 = null, e6 = n, xX = n, vz = n4(n), Q8 = E4, $3 = null, hz = n, E5 = n, Y3 = n, F5 = n, q3 = null, gQ = null, yz = 0, DO = 500, kO = 1 / 0, dT = 500, F4 = null;
    function W3() {
      kO = E8() + dT;
    }
    function RO() {
      return kO;
    }
    var U5 = !1, fz = null, cY = null, L$ = !1, JJ = null, K3 = n, mz = [], bz = null, lT = 50, H3 = 0, uz = null, cz = !1, P5 = !1, nT = 50, pY = 0, A5 = null, G3 = J6, L5 = n, jO = !1;
    function O5() {
      return FQ;
    }
    function UQ() {
      if ((L1 & (v8 | UZ)) !== t6)
        return E8();
      if (G3 !== J6)
        return G3;
      return G3 = E8(), G3;
    }
    function $J(Z) {
      var X = Z.mode;
      if ((X & A1) === B0)
        return b0;
      else if ((L1 & v8) !== t6 && e6 !== n)
        return XW(e6);
      var $ = yI() !== hI;
      if ($) {
        if (x8.transition !== null) {
          var q = x8.transition;
          if (!q._updatedFibers)
            q._updatedFibers = /* @__PURE__ */ new Set;
          q._updatedFibers.add(Z);
        }
        if (L5 === U8)
          L5 = $P();
        return L5;
      }
      var H = pZ();
      if (H !== U8)
        return H;
      var G = MS();
      return G;
    }
    function sT(Z) {
      var X = Z.mode;
      if ((X & A1) === B0)
        return b0;
      return lB();
    }
    function Z8(Z, X, $, q) {
      if (Ag(), jO)
        K("useInsertionEffect must not schedule updates.");
      if (cz)
        P5 = !0;
      if (JW(Z, $, q), (L1 & v8) !== n && Z === FQ)
        wg(X);
      else {
        if (cZ)
          WP(Z, X, $);
        if (Mg(X), Z === FQ) {
          if ((L1 & v8) === t6)
            Y3 = Q1(Y3, $);
          if (Q8 === J3)
            YJ(Z, e6);
        }
        if (xQ(Z, q), $ === b0 && L1 === t6 && (X.mode & A1) === B0 && !QX.isBatchingLegacy)
          W3(), RA();
      }
    }
    function oT(Z, X, $) {
      var q = Z.current;
      q.lanes = X, JW(Z, X, $), xQ(Z, $);
    }
    function aT(Z) {
      return (L1 & v8) !== t6;
    }
    function xQ(Z, X) {
      var $ = Z.callbackNode;
      mB(Z, X);
      var q = yK(Z, Z === FQ ? e6 : n);
      if (q === n) {
        if ($ !== null)
          uO($);
        Z.callbackNode = null, Z.callbackPriority = U8;
        return;
      }
      var H = X$(q), G = Z.callbackPriority;
      if (G === H && !(QX.current !== null && $ !== az)) {
        if ($ == null && G !== b0)
          K("Expected scheduled callback to exist. This error is likely caused by a bug in React. Please file an issue.");
        return;
      }
      if ($ != null)
        uO($);
      var E;
      if (H === b0) {
        if (Z.tag === s4) {
          if (QX.isBatchingLegacy !== null)
            QX.didScheduleLegacyUpdate = !0;
          OI(VO.bind(null, Z));
        } else
          kA(VO.bind(null, Z));
        if (QX.current !== null)
          QX.current.push(o4);
        else
          kS(function() {
            if ((L1 & (v8 | UZ)) === t6)
              o4();
          });
        E = null;
      } else {
        var U;
        switch (GP(q)) {
          case sQ:
            U = gK;
            break;
          case $4:
            U = h7;
            break;
          case Y4:
            U = tJ;
            break;
          case uK:
            U = y7;
            break;
          default:
            U = tJ;
            break;
        }
        E = rz(U, BO.bind(null, Z));
      }
      Z.callbackPriority = H, Z.callbackNode = E;
    }
    function BO(Z, X) {
      if (K_(), G3 = J6, L5 = n, (L1 & (v8 | UZ)) !== t6)
        throw new Error("Should not already be working.");
      var $ = Z.callbackNode, q = P4();
      if (q) {
        if (Z.callbackNode !== $)
          return null;
      }
      var H = yK(Z, Z === FQ ? e6 : n);
      if (H === n)
        return null;
      var G = !fK(Z, H) && !dB(Z, H) && !X, E = G ? Yg(Z, H) : M5(Z, H);
      if (E !== E4) {
        if (E === A$) {
          var U = YG(Z);
          if (U !== n)
            H = U, E = pz(Z, U);
        }
        if (E === X3) {
          var P = $3;
          throw O$(Z, n), YJ(Z, H), xQ(Z, E8()), P;
        }
        if (E === xz)
          YJ(Z, H);
        else {
          var O = !fK(Z, H), k = Z.current.alternate;
          if (O && !iT(k)) {
            if (E = M5(Z, H), E === A$) {
              var C = YG(Z);
              if (C !== n)
                H = C, E = pz(Z, C);
            }
            if (E === X3) {
              var B = $3;
              throw O$(Z, n), YJ(Z, H), xQ(Z, E8()), B;
            }
          }
          Z.finishedWork = k, Z.finishedLanes = H, rT(Z, E, H);
        }
      }
      if (xQ(Z, E8()), Z.callbackNode === $)
        return BO.bind(null, Z);
      return null;
    }
    function pz(Z, X) {
      var $ = q3;
      if (cK(Z)) {
        var q = O$(Z, X);
        q.flags |= eX, NI(Z.containerInfo);
      }
      var H = M5(Z, X);
      if (H !== A$) {
        var G = gQ;
        if (gQ = $, G !== null)
          CO(G);
      }
      return H;
    }
    function CO(Z) {
      if (gQ === null)
        gQ = Z;
      else
        gQ.push.apply(gQ, Z);
    }
    function rT(Z, X, $) {
      switch (X) {
        case E4:
        case X3:
          throw new Error("Root did not complete. This is a bug in React.");
        case A$: {
          w$(Z, gQ, F4);
          break;
        }
        case N5: {
          if (YJ(Z, $), XP($) && !cO()) {
            var q = yz + DO - E8();
            if (q > 10) {
              var H = yK(Z, n);
              if (H !== n)
                break;
              var G = Z.suspendedLanes;
              if (!EY(G, $)) {
                var E = UQ();
                qP(Z, G);
                break;
              }
              Z.timeoutHandle = mG(w$.bind(null, Z, gQ, F4), q);
              break;
            }
          }
          w$(Z, gQ, F4);
          break;
        }
        case J3: {
          if (YJ(Z, $), pB($))
            break;
          if (!cO()) {
            var U = yB(Z, $), P = U, O = E8() - P, k = Pg(O) - O;
            if (k > 10) {
              Z.timeoutHandle = mG(w$.bind(null, Z, gQ, F4), k);
              break;
            }
          }
          w$(Z, gQ, F4);
          break;
        }
        case MO: {
          w$(Z, gQ, F4);
          break;
        }
        default:
          throw new Error("Unknown root exit status.");
      }
    }
    function iT(Z) {
      var X = Z;
      while (!0) {
        if (X.flags & _K) {
          var $ = X.updateQueue;
          if ($ !== null) {
            var q = $.stores;
            if (q !== null)
              for (var H = 0;H < q.length; H++) {
                var G = q[H], E = G.getSnapshot, U = G.value;
                try {
                  if (!aQ(E(), U))
                    return !1;
                } catch (O) {
                  return !1;
                }
              }
          }
        }
        var P = X.child;
        if (X.subtreeFlags & _K && P !== null) {
          P.return = X, X = P;
          continue;
        }
        if (X === Z)
          return !0;
        while (X.sibling === null) {
          if (X.return === null || X.return === Z)
            return !0;
          X = X.return;
        }
        X.sibling.return = X.return, X = X.sibling;
      }
      return !0;
    }
    function YJ(Z, X) {
      X = mK(X, F5), X = mK(X, Y3), sB(Z, X);
    }
    function VO(Z) {
      if (H_(), (L1 & (v8 | UZ)) !== t6)
        throw new Error("Should not already be working.");
      P4();
      var X = yK(Z, n);
      if (!nQ(X, b0))
        return xQ(Z, E8()), null;
      var $ = M5(Z, X);
      if (Z.tag !== s4 && $ === A$) {
        var q = YG(Z);
        if (q !== n)
          X = q, $ = pz(Z, q);
      }
      if ($ === X3) {
        var H = $3;
        throw O$(Z, n), YJ(Z, X), xQ(Z, E8()), H;
      }
      if ($ === xz)
        throw new Error("Root did not complete. This is a bug in React.");
      var G = Z.current.alternate;
      return Z.finishedWork = G, Z.finishedLanes = X, w$(Z, gQ, F4), xQ(Z, E8()), null;
    }
    function tT(Z, X) {
      if (X !== n) {
        if (HG(Z, Q1(X, b0)), xQ(Z, E8()), (L1 & (v8 | UZ)) === t6)
          W3(), o4();
      }
    }
    function dz(Z, X) {
      var $ = L1;
      L1 |= wO;
      try {
        return Z(X);
      } finally {
        if (L1 = $, L1 === t6 && !QX.isBatchingLegacy)
          W3(), RA();
      }
    }
    function eT(Z, X, $, q, H) {
      var G = pZ(), E = x8.transition;
      try {
        return x8.transition = null, P8(sQ), Z(X, $, q, H);
      } finally {
        if (P8(G), x8.transition = E, L1 === t6)
          W3();
      }
    }
    function U4(Z) {
      if (JJ !== null && JJ.tag === s4 && (L1 & (v8 | UZ)) === t6)
        P4();
      var X = L1;
      L1 |= wO;
      var $ = x8.transition, q = pZ();
      try {
        if (x8.transition = null, P8(sQ), Z)
          return Z();
        else
          return;
      } finally {
        if (P8(q), x8.transition = $, L1 = X, (L1 & (v8 | UZ)) === t6)
          o4();
      }
    }
    function SO() {
      return (L1 & (v8 | UZ)) !== t6;
    }
    function w5(Z, X) {
      r8(vz, xX, Z), xX = Q1(xX, X), hz = Q1(hz, X);
    }
    function lz(Z) {
      xX = vz.current, a8(vz, Z);
    }
    function O$(Z, X) {
      Z.finishedWork = null, Z.finishedLanes = n;
      var $ = Z.timeoutHandle;
      if ($ !== bG)
        Z.timeoutHandle = bG, DS($);
      if (M6 !== null) {
        var q = M6.return;
        while (q !== null) {
          var H = q.alternate;
          JO(H, q), q = q.return;
        }
      }
      FQ = Z;
      var G = M$(Z.current, null);
      return M6 = G, e6 = xX = hz = X, Q8 = E4, $3 = null, E5 = n, Y3 = n, F5 = n, q3 = null, gQ = null, dI(), nZ.discardPendingWarnings(), G;
    }
    function IO(Z, X) {
      do {
        var $ = M6;
        try {
          if (V9(), eA(), N8(), gz.current = null, $ === null || $.return === null) {
            Q8 = X3, $3 = X, M6 = null;
            return;
          }
          if (N6 && $.mode & b1)
            Y5($, !0);
          if (x0)
            if (HY(), X !== null && typeof X === "object" && typeof X.then === "function") {
              var q = X;
              jB($, q, e6);
            } else
              RB($, X, e6);
          L_(Z, $.return, $, X, e6), xO($);
        } catch (H) {
          if (X = H, M6 === $ && $ !== null)
            $ = $.return, M6 = $;
          else
            $ = M6;
          continue;
        }
        return;
      } while (!0);
    }
    function _O() {
      var Z = Tz.current;
      if (Tz.current = Q5, Z === null)
        return Q5;
      else
        return Z;
    }
    function TO(Z) {
      Tz.current = Z;
    }
    function Qg() {
      yz = E8();
    }
    function z3(Z) {
      E5 = Q1(Z, E5);
    }
    function Zg() {
      if (Q8 === E4)
        Q8 = N5;
    }
    function nz() {
      if (Q8 === E4 || Q8 === N5 || Q8 === A$)
        Q8 = J3;
      if (FQ !== null && (qG(E5) || qG(Y3)))
        YJ(FQ, e6);
    }
    function Xg(Z) {
      if (Q8 !== J3)
        Q8 = A$;
      if (q3 === null)
        q3 = [Z];
      else
        q3.push(Z);
    }
    function Jg() {
      return Q8 === E4;
    }
    function M5(Z, X) {
      var $ = L1;
      L1 |= v8;
      var q = _O();
      if (FQ !== Z || e6 !== X) {
        if (cZ) {
          var H = Z.memoizedUpdaters;
          if (H.size > 0)
            N3(Z, e6), H.clear();
          KP(Z, X);
        }
        F4 = HP(), O$(Z, X);
      }
      iU(X);
      do
        try {
          $g();
          break;
        } catch (G) {
          IO(Z, G);
        }
      while (!0);
      if (V9(), L1 = $, TO(q), M6 !== null)
        throw new Error("Cannot commit an incomplete root. This error is likely caused by a bug in React. Please file an issue.");
      return tU(), FQ = null, e6 = n, Q8;
    }
    function $g() {
      while (M6 !== null)
        gO(M6);
    }
    function Yg(Z, X) {
      var $ = L1;
      L1 |= v8;
      var q = _O();
      if (FQ !== Z || e6 !== X) {
        if (cZ) {
          var H = Z.memoizedUpdaters;
          if (H.size > 0)
            N3(Z, e6), H.clear();
          KP(Z, X);
        }
        F4 = HP(), W3(), O$(Z, X);
      }
      iU(X);
      do
        try {
          qg();
          break;
        } catch (G) {
          IO(Z, G);
        }
      while (!0);
      if (V9(), TO(q), L1 = $, M6 !== null)
        return IB(), E4;
      else
        return tU(), FQ = null, e6 = n, Q8;
    }
    function qg() {
      while (M6 !== null && !$B())
        gO(M6);
    }
    function gO(Z) {
      var X = Z.alternate;
      w6(Z);
      var $;
      if ((Z.mode & b1) !== B0)
        o2(Z), $ = sz(X, Z, xX), Y5(Z, !0);
      else
        $ = sz(X, Z, xX);
      if (N8(), Z.memoizedProps = Z.pendingProps, $ === null)
        xO(Z);
      else
        M6 = $;
      gz.current = null;
    }
    function xO(Z) {
      var X = Z;
      do {
        var { alternate: $, return: q } = X;
        if ((X.flags & oq) === S0) {
          w6(X);
          var H = void 0;
          if ((X.mode & b1) === B0)
            H = XO($, X, xX);
          else
            o2(X), H = XO($, X, xX), Y5(X, !1);
          if (N8(), H !== null) {
            M6 = H;
            return;
          }
        } else {
          var G = r_($, X);
          if (G !== null) {
            G.flags &= tj, M6 = G;
            return;
          }
          if ((X.mode & b1) !== B0) {
            Y5(X, !1);
            var { actualDuration: E, child: U } = X;
            while (U !== null)
              E += U.actualDuration, U = U.sibling;
            X.actualDuration = E;
          }
          if (q !== null)
            q.flags |= oq, q.subtreeFlags = S0, q.deletions = null;
          else {
            Q8 = xz, M6 = null;
            return;
          }
        }
        var P = X.sibling;
        if (P !== null) {
          M6 = P;
          return;
        }
        X = q, M6 = X;
      } while (X !== null);
      if (Q8 === E4)
        Q8 = MO;
    }
    function w$(Z, X, $) {
      var q = pZ(), H = x8.transition;
      try {
        x8.transition = null, P8(sQ), Wg(Z, X, $, q);
      } finally {
        x8.transition = H, P8(q);
      }
      return null;
    }
    function Wg(Z, X, $, q) {
      do
        P4();
      while (JJ !== null);
      if (Lg(), (L1 & (v8 | UZ)) !== t6)
        throw new Error("Should not already be working.");
      var { finishedWork: H, finishedLanes: G } = Z;
      if (AB(G), H === null)
        return oU(), null;
      else if (G === n)
        K("root.finishedLanes should not be empty during a commit. This is a bug in React.");
      if (Z.finishedWork = null, Z.finishedLanes = n, H === Z.current)
        throw new Error("Cannot commit the same tree as before. This error is likely caused by a bug in React. Please file an issue.");
      Z.callbackNode = null, Z.callbackPriority = U8;
      var E = Q1(H.lanes, H.childLanes);
      if (oB(Z, E), Z === FQ)
        FQ = null, M6 = null, e6 = n;
      if ((H.subtreeFlags & KY) !== S0 || (H.flags & KY) !== S0) {
        if (!L$)
          L$ = !0, bz = $, rz(tJ, function() {
            return P4(), null;
          });
      }
      var U = (H.subtreeFlags & (x7 | v7 | aq | KY)) !== S0, P = (H.flags & (x7 | v7 | aq | KY)) !== S0;
      if (U || P) {
        var O = x8.transition;
        x8.transition = null;
        var k = pZ();
        P8(sQ);
        var C = L1;
        L1 |= UZ, gz.current = null;
        var B = ZT(Z, H);
        RL(), UT(Z, H, G), US(Z.containerInfo), Z.current = H, BB(G), PT(H, Z, G), CB(), YB(), L1 = C, P8(k), x8.transition = O;
      } else
        Z.current = H, RL();
      var v = L$;
      if (L$)
        L$ = !1, JJ = Z, K3 = G;
      else
        pY = 0, A5 = null;
      if (E = Z.pendingLanes, E === n)
        cY = null;
      if (!v)
        fO(Z.current, !1);
      if (NB(H.stateNode, q), cZ)
        Z.memoizedUpdaters.clear();
      if (bT(), xQ(Z, E8()), X !== null) {
        var h = Z.onRecoverableError;
        for (var f = 0;f < X.length; f++) {
          var q0 = X[f], k0 = q0.stack, w0 = q0.digest;
          h(q0.value, {
            componentStack: k0,
            digest: w0
          });
        }
      }
      if (U5) {
        U5 = !1;
        var N1 = fz;
        throw fz = null, N1;
      }
      if (nQ(K3, b0) && Z.tag !== s4)
        P4();
      if (E = Z.pendingLanes, nQ(E, b0))
        if (W_(), Z === uz)
          H3++;
        else
          H3 = 0, uz = Z;
      else
        H3 = 0;
      return o4(), oU(), null;
    }
    function P4() {
      if (JJ !== null) {
        var Z = GP(K3), X = tB(Y4, Z), $ = x8.transition, q = pZ();
        try {
          return x8.transition = null, P8(X), Hg();
        } finally {
          P8(q), x8.transition = $;
        }
      }
      return !1;
    }
    function Kg(Z) {
      if (mz.push(Z), !L$)
        L$ = !0, rz(tJ, function() {
          return P4(), null;
        });
    }
    function Hg() {
      if (JJ === null)
        return !1;
      var Z = bz;
      bz = null;
      var X = JJ, $ = K3;
      if (JJ = null, K3 = n, (L1 & (v8 | UZ)) !== t6)
        throw new Error("Cannot flush passive effects while already rendering.");
      cz = !0, P5 = !1, VB($);
      var q = L1;
      L1 |= UZ, kT(X.current), OT(X, X.current, $, Z);
      {
        var H = mz;
        mz = [];
        for (var G = 0;G < H.length; G++) {
          var E = H[G];
          YT(X, E);
        }
      }
      SB(), fO(X.current, !0), L1 = q, o4();
      {
        if (P5)
          if (X === A5)
            pY++;
          else
            pY = 0, A5 = X;
        else
          pY = 0;
        cz = !1, P5 = !1;
      }
      EB(X);
      {
        var U = X.current.stateNode;
        U.effectDuration = 0, U.passiveEffectDuration = 0;
      }
      return !0;
    }
    function vO(Z) {
      return cY !== null && cY.has(Z);
    }
    function Gg(Z) {
      if (cY === null)
        cY = /* @__PURE__ */ new Set([Z]);
      else
        cY.add(Z);
    }
    function zg(Z) {
      if (!U5)
        U5 = !0, fz = Z;
    }
    var Ng = zg;
    function hO(Z, X, $) {
      var q = U$($, X), H = TL(Z, q, b0), G = r4(Z, H, b0), E = UQ();
      if (G !== null)
        JW(G, b0, E), xQ(G, E);
    }
    function Z6(Z, X, $) {
      if (t_($), E3(!1), Z.tag === w) {
        hO(Z, Z, $);
        return;
      }
      var q = null;
      q = X;
      while (q !== null) {
        if (q.tag === w) {
          hO(q, Z, $);
          return;
        } else if (q.tag === F) {
          var { type: H, stateNode: G } = q;
          if (typeof H.getDerivedStateFromError === "function" || typeof G.componentDidCatch === "function" && !vO(G)) {
            var E = U$($, Z), U = Nz(q, E, b0), P = r4(q, U, b0), O = UQ();
            if (P !== null)
              JW(P, b0, O), xQ(P, O);
            return;
          }
        }
        q = q.return;
      }
      K(`Internal React error: Attempted to capture a commit phase error inside a detached tree. This indicates a bug in React. Likely causes include deleting the same fiber more than once, committing an already-finished tree, or an inconsistent return pointer.

Error message:

%s`, $);
    }
    function Eg(Z, X, $) {
      var q = Z.pingCache;
      if (q !== null)
        q.delete(X);
      var H = UQ();
      if (qP(Z, $), Dg(Z), FQ === Z && EY(e6, $))
        if (Q8 === J3 || Q8 === N5 && XP(e6) && E8() - yz < DO)
          O$(Z, n);
        else
          F5 = Q1(F5, $);
      xQ(Z, H);
    }
    function yO(Z, X) {
      if (X === U8)
        X = sT(Z);
      var $ = UQ(), q = _Q(Z, X);
      if (q !== null)
        JW(q, X, $), xQ(q, $);
    }
    function Fg(Z) {
      var X = Z.memoizedState, $ = U8;
      if (X !== null)
        $ = X.retryLane;
      yO(Z, $);
    }
    function Ug(Z, X) {
      var $ = U8, q;
      switch (Z.tag) {
        case l:
          q = Z.stateNode;
          var H = Z.memoizedState;
          if (H !== null)
            $ = H.retryLane;
          break;
        case p:
          q = Z.stateNode;
          break;
        default:
          throw new Error("Pinged unknown suspense boundary type. This is probably a bug in React.");
      }
      if (q !== null)
        q.delete(X);
      yO(Z, $);
    }
    function Pg(Z) {
      return Z < 120 ? 120 : Z < 480 ? 480 : Z < 1080 ? 1080 : Z < 1920 ? 1920 : Z < 3000 ? 3000 : Z < 4320 ? 4320 : pT(Z / 1960) * 1960;
    }
    function Ag() {
      if (H3 > lT)
        throw H3 = 0, uz = null, new Error("Maximum update depth exceeded. This can happen when a component repeatedly calls setState inside componentWillUpdate or componentDidUpdate. React limits the number of nested updates to prevent infinite loops.");
      if (pY > nT)
        pY = 0, A5 = null, K("Maximum update depth exceeded. This can happen when a component calls setState inside useEffect, but useEffect either doesn't have a dependency array, or one of the dependencies changes on every render.");
    }
    function Lg() {
      nZ.flushLegacyContextWarning(), nZ.flushPendingUnsafeLifecycleWarnings();
    }
    function fO(Z, X) {
      {
        if (w6(Z), D5(Z, Z4, TT), X)
          D5(Z, TK, gT);
        if (D5(Z, Z4, IT), X)
          D5(Z, TK, _T);
        N8();
      }
    }
    function D5(Z, X, $) {
      {
        var q = Z, H = null;
        while (q !== null) {
          var G = q.subtreeFlags & X;
          if (q !== H && q.child !== null && G !== S0)
            q = q.child;
          else {
            if ((q.flags & X) !== S0)
              $(q);
            if (q.sibling !== null)
              q = q.sibling;
            else
              q = H = q.return;
          }
        }
      }
    }
    var k5 = null;
    function mO(Z) {
      {
        if ((L1 & v8) !== t6)
          return;
        if (!(Z.mode & A1))
          return;
        var X = Z.tag;
        if (X !== L && X !== w && X !== F && X !== N && X !== r && X !== t && X !== $0)
          return;
        var $ = V0(Z) || "ReactComponent";
        if (k5 !== null) {
          if (k5.has($))
            return;
          k5.add($);
        } else
          k5 = /* @__PURE__ */ new Set([$]);
        var q = z8;
        try {
          w6(Z), K("Can't perform a React state update on a component that hasn't mounted yet. This indicates that you have a side-effect in your render function that asynchronously later calls tries to update the component. Move this work to useEffect instead.");
        } finally {
          if (q)
            w6(Z);
          else
            N8();
        }
      }
    }
    var sz;
    {
      var Og = null;
      sz = function(Z, X, $) {
        var q = sO(Og, X);
        try {
          return iL(Z, X, $);
        } catch (G) {
          if (CI() || G !== null && typeof G === "object" && typeof G.then === "function")
            throw G;
          if (V9(), eA(), JO(Z, X), sO(X, q), X.mode & b1)
            o2(X);
          if (V7(null, iL, null, Z, X, $), oj()) {
            var H = S7();
            if (typeof H === "object" && H !== null && H._suppressLogging && typeof G === "object" && G !== null && !G._suppressLogging)
              G._suppressLogging = !0;
          }
          throw G;
        }
      };
    }
    var bO = !1, oz;
    oz = /* @__PURE__ */ new Set;
    function wg(Z) {
      if (MX && !$_())
        switch (Z.tag) {
          case N:
          case r:
          case $0: {
            var X = M6 && V0(M6) || "Unknown", $ = X;
            if (!oz.has($)) {
              oz.add($);
              var q = V0(Z) || "Unknown";
              K("Cannot update a component (`%s`) while rendering a different component (`%s`). To locate the bad setState() call inside `%s`, follow the stack trace as described in https://reactjs.org/link/setstate-in-render", q, X, X);
            }
            break;
          }
          case F: {
            if (!bO)
              K("Cannot update during an existing state transition (such as within `render`). Render methods should be a pure function of props and state."), bO = !0;
            break;
          }
        }
    }
    function N3(Z, X) {
      if (cZ) {
        var $ = Z.memoizedUpdaters;
        $.forEach(function(q) {
          WP(Z, q, X);
        });
      }
    }
    var az = {};
    function rz(Z, X) {
      {
        var $ = QX.current;
        if ($ !== null)
          return $.push(X), az;
        else
          return sU(Z, X);
      }
    }
    function uO(Z) {
      if (Z === az)
        return;
      return JB(Z);
    }
    function cO() {
      return QX.current !== null;
    }
    function Mg(Z) {
      {
        if (Z.mode & A1) {
          if (!OO())
            return;
        } else {
          if (!cT())
            return;
          if (L1 !== t6)
            return;
          if (Z.tag !== N && Z.tag !== r && Z.tag !== $0)
            return;
        }
        if (QX.current === null) {
          var X = z8;
          try {
            w6(Z), K(`An update to %s inside a test was not wrapped in act(...).

When testing, code that causes React state updates should be wrapped into act(...):

act(() => {
  /* fire events that update state */
});
/* assert on the output */

This ensures that you're testing the behavior the user would see in the browser. Learn more at https://reactjs.org/link/wrap-tests-with-act`, V0(Z));
          } finally {
            if (X)
              w6(Z);
            else
              N8();
          }
        }
      }
    }
    function Dg(Z) {
      if (Z.tag !== s4 && OO() && QX.current === null)
        K(`A suspended resource finished loading inside a test, but the event was not wrapped in act(...).

When testing, code that resolves suspended data should be wrapped into act(...):

act(() => {
  /* finish loading suspended data */
});
/* assert on the output */

This ensures that you're testing the behavior the user would see in the browser. Learn more at https://reactjs.org/link/wrap-tests-with-act`);
    }
    function E3(Z) {
      jO = Z;
    }
    var PZ = null, dY = null, kg = function(Z) {
      PZ = Z;
    };
    function lY(Z) {
      {
        if (PZ === null)
          return Z;
        var X = PZ(Z);
        if (X === void 0)
          return Z;
        return X.current;
      }
    }
    function iz(Z) {
      return lY(Z);
    }
    function tz(Z) {
      {
        if (PZ === null)
          return Z;
        var X = PZ(Z);
        if (X === void 0) {
          if (Z !== null && Z !== void 0 && typeof Z.render === "function") {
            var $ = lY(Z.render);
            if (Z.render !== $) {
              var q = {
                $$typeof: V1,
                render: $
              };
              if (Z.displayName !== void 0)
                q.displayName = Z.displayName;
              return q;
            }
          }
          return Z;
        }
        return X.current;
      }
    }
    function pO(Z, X) {
      {
        if (PZ === null)
          return !1;
        var $ = Z.elementType, q = X.type, H = !1, G = typeof q === "object" && q !== null ? q.$$typeof : null;
        switch (Z.tag) {
          case F: {
            if (typeof q === "function")
              H = !0;
            break;
          }
          case N: {
            if (typeof q === "function")
              H = !0;
            else if (G === n6)
              H = !0;
            break;
          }
          case r: {
            if (G === V1)
              H = !0;
            else if (G === n6)
              H = !0;
            break;
          }
          case t:
          case $0: {
            if (G === nX)
              H = !0;
            else if (G === n6)
              H = !0;
            break;
          }
          default:
            return !1;
        }
        if (H) {
          var E = PZ($);
          if (E !== void 0 && E === PZ(q))
            return !0;
        }
        return !1;
      }
    }
    function dO(Z) {
      {
        if (PZ === null)
          return;
        if (typeof WeakSet !== "function")
          return;
        if (dY === null)
          dY = /* @__PURE__ */ new WeakSet;
        dY.add(Z);
      }
    }
    var Rg = function(Z, X) {
      {
        if (PZ === null)
          return;
        var { staleFamilies: $, updatedFamilies: q } = X;
        P4(), U4(function() {
          ez(Z.current, q, $);
        });
      }
    }, jg = function(Z, X) {
      {
        if (Z.context !== rQ)
          return;
        P4(), U4(function() {
          F3(X, Z, null, null);
        });
      }
    };
    function ez(Z, X, $) {
      {
        var { alternate: q, child: H, sibling: G, tag: E, type: U } = Z, P = null;
        switch (E) {
          case N:
          case $0:
          case F:
            P = U;
            break;
          case r:
            P = U.render;
            break;
        }
        if (PZ === null)
          throw new Error("Expected resolveFamily to be set during hot reload.");
        var O = !1, k = !1;
        if (P !== null) {
          var C = PZ(P);
          if (C !== void 0) {
            if ($.has(C))
              k = !0;
            else if (X.has(C))
              if (E === F)
                k = !0;
              else
                O = !0;
          }
        }
        if (dY !== null) {
          if (dY.has(Z) || q !== null && dY.has(q))
            k = !0;
        }
        if (k)
          Z._debugNeedsRemount = !0;
        if (k || O) {
          var B = _Q(Z, b0);
          if (B !== null)
            Z8(B, Z, b0, J6);
        }
        if (H !== null && !k)
          ez(H, X, $);
        if (G !== null)
          ez(G, X, $);
      }
    }
    var Bg = function(Z, X) {
      {
        var $ = /* @__PURE__ */ new Set, q = new Set(X.map(function(H) {
          return H.current;
        }));
        return QN(Z.current, q, $), $;
      }
    };
    function QN(Z, X, $) {
      {
        var { child: q, sibling: H, tag: G, type: E } = Z, U = null;
        switch (G) {
          case N:
          case $0:
          case F:
            U = E;
            break;
          case r:
            U = E.render;
            break;
        }
        var P = !1;
        if (U !== null) {
          if (X.has(U))
            P = !0;
        }
        if (P)
          Cg(Z, $);
        else if (q !== null)
          QN(q, X, $);
        if (H !== null)
          QN(H, X, $);
      }
    }
    function Cg(Z, X) {
      {
        var $ = Vg(Z, X);
        if ($)
          return;
        var q = Z;
        while (!0) {
          switch (q.tag) {
            case R:
              X.add(q.stateNode);
              return;
            case D:
              X.add(q.stateNode.containerInfo);
              return;
            case w:
              X.add(q.stateNode.containerInfo);
              return;
          }
          if (q.return === null)
            throw new Error("Expected to reach root first.");
          q = q.return;
        }
      }
    }
    function Vg(Z, X) {
      {
        var $ = Z, q = !1;
        while (!0) {
          if ($.tag === R)
            q = !0, X.add($.stateNode);
          else if ($.child !== null) {
            $.child.return = $, $ = $.child;
            continue;
          }
          if ($ === Z)
            return q;
          while ($.sibling === null) {
            if ($.return === null || $.return === Z)
              return q;
            $ = $.return;
          }
          $.sibling.return = $.return, $ = $.sibling;
        }
      }
      return !1;
    }
    var ZN;
    {
      ZN = !1;
      try {
        var lO = Object.preventExtensions({});
        ;
      } catch (Z) {
        ZN = !0;
      }
    }
    function Sg(Z, X, $, q) {
      if (this.tag = Z, this.key = $, this.elementType = null, this.type = null, this.stateNode = null, this.return = null, this.child = null, this.sibling = null, this.index = 0, this.ref = null, this.pendingProps = X, this.memoizedProps = null, this.updateQueue = null, this.memoizedState = null, this.dependencies = null, this.mode = q, this.flags = S0, this.subtreeFlags = S0, this.deletions = null, this.lanes = n, this.childLanes = n, this.alternate = null, this.actualDuration = Number.NaN, this.actualStartTime = Number.NaN, this.selfBaseDuration = Number.NaN, this.treeBaseDuration = Number.NaN, this.actualDuration = 0, this.actualStartTime = -1, this.selfBaseDuration = 0, this.treeBaseDuration = 0, this._debugSource = null, this._debugOwner = null, this._debugNeedsRemount = !1, this._debugHookTypes = null, !ZN && typeof Object.preventExtensions === "function")
        Object.preventExtensions(this);
    }
    var iQ = function(Z, X, $, q) {
      return new Sg(Z, X, $, q);
    };
    function XN(Z) {
      var X = Z.prototype;
      return !!(X && X.isReactComponent);
    }
    function Ig(Z) {
      return typeof Z === "function" && !XN(Z) && Z.defaultProps === void 0;
    }
    function _g(Z) {
      if (typeof Z === "function")
        return XN(Z) ? F : N;
      else if (Z !== void 0 && Z !== null) {
        var X = Z.$$typeof;
        if (X === V1)
          return r;
        if (X === nX)
          return t;
      }
      return L;
    }
    function M$(Z, X) {
      var $ = Z.alternate;
      if ($ === null)
        $ = iQ(Z.tag, X, Z.key, Z.mode), $.elementType = Z.elementType, $.type = Z.type, $.stateNode = Z.stateNode, $._debugSource = Z._debugSource, $._debugOwner = Z._debugOwner, $._debugHookTypes = Z._debugHookTypes, $.alternate = Z, Z.alternate = $;
      else
        $.pendingProps = X, $.type = Z.type, $.flags = S0, $.subtreeFlags = S0, $.deletions = null, $.actualDuration = 0, $.actualStartTime = -1;
      $.flags = Z.flags & X4, $.childLanes = Z.childLanes, $.lanes = Z.lanes, $.child = Z.child, $.memoizedProps = Z.memoizedProps, $.memoizedState = Z.memoizedState, $.updateQueue = Z.updateQueue;
      var q = Z.dependencies;
      switch ($.dependencies = q === null ? null : {
        lanes: q.lanes,
        firstContext: q.firstContext
      }, $.sibling = Z.sibling, $.index = Z.index, $.ref = Z.ref, $.selfBaseDuration = Z.selfBaseDuration, $.treeBaseDuration = Z.treeBaseDuration, $._debugNeedsRemount = Z._debugNeedsRemount, $.tag) {
        case L:
        case N:
        case $0:
          $.type = lY(Z.type);
          break;
        case F:
          $.type = iz(Z.type);
          break;
        case r:
          $.type = tz(Z.type);
          break;
      }
      return $;
    }
    function Tg(Z, X) {
      Z.flags &= X4 | m6;
      var $ = Z.alternate;
      if ($ === null)
        Z.childLanes = n, Z.lanes = X, Z.child = null, Z.subtreeFlags = S0, Z.memoizedProps = null, Z.memoizedState = null, Z.updateQueue = null, Z.dependencies = null, Z.stateNode = null, Z.selfBaseDuration = 0, Z.treeBaseDuration = 0;
      else {
        Z.childLanes = $.childLanes, Z.lanes = $.lanes, Z.child = $.child, Z.subtreeFlags = S0, Z.deletions = null, Z.memoizedProps = $.memoizedProps, Z.memoizedState = $.memoizedState, Z.updateQueue = $.updateQueue, Z.type = $.type;
        var q = $.dependencies;
        Z.dependencies = q === null ? null : {
          lanes: q.lanes,
          firstContext: q.firstContext
        }, Z.selfBaseDuration = $.selfBaseDuration, Z.treeBaseDuration = $.treeBaseDuration;
      }
      return Z;
    }
    function gg(Z, X, $) {
      var q;
      if (Z === L9) {
        if (q = A1, X === !0)
          q |= j6, q |= RX;
      } else
        q = B0;
      if (cZ)
        q |= b1;
      return iQ(w, null, null, q);
    }
    function JN(Z, X, $, q, H, G) {
      var E = L, U = Z;
      if (typeof Z === "function")
        if (XN(Z))
          E = F, U = iz(U);
        else
          U = lY(U);
      else if (typeof Z === "string")
        E = R;
      else
        Q:
          switch (Z) {
            case KQ:
              return qJ($.children, H, G, X);
            case PX:
              if (E = s, H |= j6, (H & A1) !== B0)
                H |= RX;
              break;
            case pQ:
              return xg($, H, G, X);
            case V4:
              return vg($, H, G, X);
            case S4:
              return hg($, H, G, X);
            case s$:
              return nO($, H, G, X);
            case hq:
            case xq:
            case yq:
            case fq:
            case vq:
            default: {
              if (typeof Z === "object" && Z !== null)
                switch (Z.$$typeof) {
                  case HQ:
                    E = F0;
                    break Q;
                  case fZ:
                    E = i;
                    break Q;
                  case V1:
                    E = r, U = tz(U);
                    break Q;
                  case nX:
                    E = t;
                    break Q;
                  case n6:
                    E = M0, U = null;
                    break Q;
                }
              var P = "";
              {
                if (Z === void 0 || typeof Z === "object" && Z !== null && Object.keys(Z).length === 0)
                  P += " You likely forgot to export your component from the file it's defined in, or you might have mixed up default and named imports.";
                var O = q ? V0(q) : null;
                if (O)
                  P += `

Check the render method of \`` + O + "`.";
              }
              throw new Error("Element type is invalid: expected a string (for built-in components) or a class/function (for composite components) " + ("but got: " + (Z == null ? Z : typeof Z) + "." + P));
            }
          }
      var k = iQ(E, $, X, H);
      return k.elementType = Z, k.type = U, k.lanes = G, k._debugOwner = q, k;
    }
    function $N(Z, X, $) {
      var q = null;
      q = Z._owner;
      var { type: H, key: G, props: E } = Z, U = JN(H, G, E, q, X, $);
      return U._debugSource = Z._source, U._debugOwner = Z._owner, U;
    }
    function qJ(Z, X, $, q) {
      var H = iQ(g, Z, q, X);
      return H.lanes = $, H;
    }
    function xg(Z, X, $, q) {
      if (typeof Z.id !== "string")
        K('Profiler must specify an "id" of type `string` as a prop. Received the type `%s` instead.', typeof Z.id);
      var H = iQ(J0, Z, q, X | b1);
      return H.elementType = pQ, H.lanes = $, H.stateNode = {
        effectDuration: 0,
        passiveEffectDuration: 0
      }, H;
    }
    function vg(Z, X, $, q) {
      var H = iQ(l, Z, q, X);
      return H.elementType = V4, H.lanes = $, H;
    }
    function hg(Z, X, $, q) {
      var H = iQ(p, Z, q, X);
      return H.elementType = S4, H.lanes = $, H;
    }
    function nO(Z, X, $, q) {
      var H = iQ(Y0, Z, q, X);
      H.elementType = s$, H.lanes = $;
      var G = {
        isHidden: !1
      };
      return H.stateNode = G, H;
    }
    function YN(Z, X, $) {
      var q = iQ(V, Z, null, X);
      return q.lanes = $, q;
    }
    function yg() {
      var Z = iQ(R, null, null, B0);
      return Z.elementType = "DELETED", Z;
    }
    function fg(Z) {
      var X = iQ(I0, null, null, B0);
      return X.stateNode = Z, X;
    }
    function qN(Z, X, $) {
      var q = Z.children !== null ? Z.children : [], H = iQ(D, q, Z.key, X);
      return H.lanes = $, H.stateNode = {
        containerInfo: Z.containerInfo,
        pendingChildren: null,
        implementation: Z.implementation
      }, H;
    }
    function sO(Z, X) {
      if (Z === null)
        Z = iQ(L, null, null, B0);
      return Z.tag = X.tag, Z.key = X.key, Z.elementType = X.elementType, Z.type = X.type, Z.stateNode = X.stateNode, Z.return = X.return, Z.child = X.child, Z.sibling = X.sibling, Z.index = X.index, Z.ref = X.ref, Z.pendingProps = X.pendingProps, Z.memoizedProps = X.memoizedProps, Z.updateQueue = X.updateQueue, Z.memoizedState = X.memoizedState, Z.dependencies = X.dependencies, Z.mode = X.mode, Z.flags = X.flags, Z.subtreeFlags = X.subtreeFlags, Z.deletions = X.deletions, Z.lanes = X.lanes, Z.childLanes = X.childLanes, Z.alternate = X.alternate, Z.actualDuration = X.actualDuration, Z.actualStartTime = X.actualStartTime, Z.selfBaseDuration = X.selfBaseDuration, Z.treeBaseDuration = X.treeBaseDuration, Z._debugSource = X._debugSource, Z._debugOwner = X._debugOwner, Z._debugNeedsRemount = X._debugNeedsRemount, Z._debugHookTypes = X._debugHookTypes, Z;
    }
    function mg(Z, X, $, q, H) {
      this.tag = X, this.containerInfo = Z, this.pendingChildren = null, this.current = null, this.pingCache = null, this.finishedWork = null, this.timeoutHandle = bG, this.context = null, this.pendingContext = null, this.callbackNode = null, this.callbackPriority = U8, this.eventTimes = KG(n), this.expirationTimes = KG(J6), this.pendingLanes = n, this.suspendedLanes = n, this.pingedLanes = n, this.expiredLanes = n, this.mutableReadLanes = n, this.finishedLanes = n, this.entangledLanes = n, this.entanglements = KG(n), this.identifierPrefix = q, this.onRecoverableError = H, this.mutableSourceEagerHydrationData = null, this.effectDuration = 0, this.passiveEffectDuration = 0;
      {
        this.memoizedUpdaters = /* @__PURE__ */ new Set;
        var G = this.pendingUpdatersLaneMap = [];
        for (var E = 0;E < m7; E++)
          G.push(/* @__PURE__ */ new Set);
      }
      switch (X) {
        case L9:
          this._debugRootType = $ ? "hydrateRoot()" : "createRoot()";
          break;
        case s4:
          this._debugRootType = $ ? "hydrate()" : "render()";
          break;
      }
    }
    function oO(Z, X, $, q, H, G, E, U, P, O) {
      var k = new mg(Z, X, $, U, P), C = gg(X, G);
      k.current = C, C.stateNode = k;
      {
        var B = {
          element: q,
          isDehydrated: $,
          cache: null,
          transitions: null,
          pendingSuspenseBoundaries: null
        };
        C.memoizedState = B;
      }
      return A2(C), k;
    }
    var WN = "18.3.1";
    function bg(Z, X, $) {
      var q = arguments.length > 3 && arguments[3] !== void 0 ? arguments[3] : null;
      return c8(q), {
        $$typeof: o8,
        key: q == null ? null : "" + q,
        children: Z,
        containerInfo: X,
        implementation: $
      };
    }
    var KN, HN;
    KN = !1, HN = {};
    function aO(Z) {
      if (!Z)
        return rQ;
      var X = qY(Z), $ = LI(X);
      if (X.tag === F) {
        var q = X.type;
        if (CX(q))
          return MA(X, q, $);
      }
      return $;
    }
    function ug(Z, X) {
      {
        var $ = qY(Z);
        if ($ === void 0)
          if (typeof Z.render === "function")
            throw new Error("Unable to find node on an unmounted component.");
          else {
            var q = Object.keys(Z).join(",");
            throw new Error("Argument appears to not be a ReactComponent. Keys: " + q);
          }
        var H = dU($);
        if (H === null)
          return null;
        if (H.mode & j6) {
          var G = V0($) || "Component";
          if (!HN[G]) {
            HN[G] = !0;
            var E = z8;
            try {
              if (w6(H), $.mode & j6)
                K("%s is deprecated in StrictMode. %s was passed an instance of %s which is inside StrictMode. Instead, add a ref directly to the element you want to reference. Learn more about using refs safely here: https://reactjs.org/link/strict-mode-find-node", X, X, G);
              else
                K("%s is deprecated in StrictMode. %s was passed an instance of %s which renders StrictMode children. Instead, add a ref directly to the element you want to reference. Learn more about using refs safely here: https://reactjs.org/link/strict-mode-find-node", X, X, G);
            } finally {
              if (E)
                w6(E);
              else
                N8();
            }
          }
        }
        return H.stateNode;
      }
    }
    function rO(Z, X, $, q, H, G, E, U) {
      var P = !1, O = null;
      return oO(Z, X, P, O, $, q, H, G, E);
    }
    function iO(Z, X, $, q, H, G, E, U, P, O) {
      var k = !0, C = oO($, q, k, Z, H, G, E, U, P);
      C.context = aO(null);
      var B = C.current, v = UQ(), h = $J(B), f = z4(v, h);
      return f.callback = X !== void 0 && X !== null ? X : null, r4(B, f, h), oT(C, h, v), C;
    }
    function F3(Z, X, $, q) {
      zB(X, Z);
      var H = X.current, G = UQ(), E = $J(H);
      _B(E);
      var U = aO($);
      if (X.context === null)
        X.context = U;
      else
        X.pendingContext = U;
      if (MX && z8 !== null && !KN)
        KN = !0, K(`Render methods should be a pure function of props and state; triggering nested component updates from render is not allowed. If necessary, trigger nested updates in componentDidUpdate.

Check the render method of %s.`, V0(z8) || "Unknown");
      var P = z4(G, E);
      if (P.payload = {
        element: Z
      }, q = q === void 0 ? null : q, q !== null) {
        if (typeof q !== "function")
          K("render(...): Expected the last optional `callback` argument to be a function. Instead received: %s.", q);
        P.callback = q;
      }
      var O = r4(H, P, E);
      if (O !== null)
        Z8(O, H, E, G), g9(O, H, E);
      return E;
    }
    function R5(Z) {
      var X = Z.current;
      if (!X.child)
        return null;
      switch (X.child.tag) {
        case R:
          return yG(X.child.stateNode);
        default:
          return X.child.stateNode;
      }
    }
    function cg(Z) {
      switch (Z.tag) {
        case w: {
          var X = Z.stateNode;
          if (cK(X)) {
            var $ = bB(X);
            tT(X, $);
          }
          break;
        }
        case l: {
          U4(function() {
            var H = _Q(Z, b0);
            if (H !== null) {
              var G = UQ();
              Z8(H, Z, b0, G);
            }
          });
          var q = b0;
          GN(Z, q);
          break;
        }
      }
    }
    function tO(Z, X) {
      var $ = Z.memoizedState;
      if ($ !== null && $.dehydrated !== null)
        $.retryLane = nB($.retryLane, X);
    }
    function GN(Z, X) {
      tO(Z, X);
      var $ = Z.alternate;
      if ($)
        tO($, X);
    }
    function pg(Z) {
      if (Z.tag !== l)
        return;
      var X = eq, $ = _Q(Z, X);
      if ($ !== null) {
        var q = UQ();
        Z8($, Z, X, q);
      }
      GN(Z, X);
    }
    function dg(Z) {
      if (Z.tag !== l)
        return;
      var X = $J(Z), $ = _Q(Z, X);
      if ($ !== null) {
        var q = UQ();
        Z8($, Z, X, q);
      }
      GN(Z, X);
    }
    function eO(Z) {
      var X = XB(Z);
      if (X === null)
        return null;
      return X.stateNode;
    }
    var Qw = function(Z) {
      return null;
    };
    function lg(Z) {
      return Qw(Z);
    }
    var Zw = function(Z) {
      return !1;
    };
    function ng(Z) {
      return Zw(Z);
    }
    var Xw = null, Jw = null, $w = null, Yw = null, qw = null, Ww = null, Kw = null, Hw = null, Gw = null;
    {
      var zw = function(Z, X, $) {
        var q = X[$], H = S1(Z) ? Z.slice() : K1({}, Z);
        if ($ + 1 === X.length) {
          if (S1(H))
            H.splice(q, 1);
          else
            delete H[q];
          return H;
        }
        return H[q] = zw(Z[q], X, $ + 1), H;
      }, Nw = function(Z, X) {
        return zw(Z, X, 0);
      }, Ew = function(Z, X, $, q) {
        var H = X[q], G = S1(Z) ? Z.slice() : K1({}, Z);
        if (q + 1 === X.length) {
          var E = $[q];
          if (G[E] = G[H], S1(G))
            G.splice(H, 1);
          else
            delete G[H];
        } else
          G[H] = Ew(Z[H], X, $, q + 1);
        return G;
      }, Fw = function(Z, X, $) {
        if (X.length !== $.length) {
          W("copyWithRename() expects paths of the same length");
          return;
        } else
          for (var q = 0;q < $.length - 1; q++)
            if (X[q] !== $[q]) {
              W("copyWithRename() expects paths to be the same except for the deepest key");
              return;
            }
        return Ew(Z, X, $, 0);
      }, Uw = function(Z, X, $, q) {
        if ($ >= X.length)
          return q;
        var H = X[$], G = S1(Z) ? Z.slice() : K1({}, Z);
        return G[H] = Uw(Z[H], X, $ + 1, q), G;
      }, Pw = function(Z, X, $) {
        return Uw(Z, X, 0, $);
      }, zN = function(Z, X) {
        var $ = Z.memoizedState;
        while ($ !== null && X > 0)
          $ = $.next, X--;
        return $;
      };
      Xw = function(Z, X, $, q) {
        var H = zN(Z, X);
        if (H !== null) {
          var G = Pw(H.memoizedState, $, q);
          H.memoizedState = G, H.baseState = G, Z.memoizedProps = K1({}, Z.memoizedProps);
          var E = _Q(Z, b0);
          if (E !== null)
            Z8(E, Z, b0, J6);
        }
      }, Jw = function(Z, X, $) {
        var q = zN(Z, X);
        if (q !== null) {
          var H = Nw(q.memoizedState, $);
          q.memoizedState = H, q.baseState = H, Z.memoizedProps = K1({}, Z.memoizedProps);
          var G = _Q(Z, b0);
          if (G !== null)
            Z8(G, Z, b0, J6);
        }
      }, $w = function(Z, X, $, q) {
        var H = zN(Z, X);
        if (H !== null) {
          var G = Fw(H.memoizedState, $, q);
          H.memoizedState = G, H.baseState = G, Z.memoizedProps = K1({}, Z.memoizedProps);
          var E = _Q(Z, b0);
          if (E !== null)
            Z8(E, Z, b0, J6);
        }
      }, Yw = function(Z, X, $) {
        if (Z.pendingProps = Pw(Z.memoizedProps, X, $), Z.alternate)
          Z.alternate.pendingProps = Z.pendingProps;
        var q = _Q(Z, b0);
        if (q !== null)
          Z8(q, Z, b0, J6);
      }, qw = function(Z, X) {
        if (Z.pendingProps = Nw(Z.memoizedProps, X), Z.alternate)
          Z.alternate.pendingProps = Z.pendingProps;
        var $ = _Q(Z, b0);
        if ($ !== null)
          Z8($, Z, b0, J6);
      }, Ww = function(Z, X, $) {
        if (Z.pendingProps = Fw(Z.memoizedProps, X, $), Z.alternate)
          Z.alternate.pendingProps = Z.pendingProps;
        var q = _Q(Z, b0);
        if (q !== null)
          Z8(q, Z, b0, J6);
      }, Kw = function(Z) {
        var X = _Q(Z, b0);
        if (X !== null)
          Z8(X, Z, b0, J6);
      }, Hw = function(Z) {
        Qw = Z;
      }, Gw = function(Z) {
        Zw = Z;
      };
    }
    function sg(Z) {
      var X = dU(Z);
      if (X === null)
        return null;
      return X.stateNode;
    }
    function og(Z) {
      return null;
    }
    function ag() {
      return z8;
    }
    function rg(Z) {
      var X = Z.findFiberByHostInstance, $ = Q.ReactCurrentDispatcher;
      return GB({
        bundleType: Z.bundleType,
        version: Z.version,
        rendererPackageName: Z.rendererPackageName,
        rendererConfig: Z.rendererConfig,
        overrideHookState: Xw,
        overrideHookStateDeletePath: Jw,
        overrideHookStateRenamePath: $w,
        overrideProps: Yw,
        overridePropsDeletePath: qw,
        overridePropsRenamePath: Ww,
        setErrorHandler: Hw,
        setSuspenseHandler: Gw,
        scheduleUpdate: Kw,
        currentDispatcherRef: $,
        findHostInstanceByFiber: sg,
        findFiberByHostInstance: X || og,
        findHostInstancesForRefresh: Bg,
        scheduleRefresh: Rg,
        scheduleRoot: jg,
        setRefreshHandler: kg,
        getCurrentFiber: ag,
        reconcilerVersion: WN
      });
    }
    var Aw = typeof reportError === "function" ? reportError : function(Z) {
      console.error(Z);
    };
    function NN(Z) {
      this._internalRoot = Z;
    }
    j5.prototype.render = NN.prototype.render = function(Z) {
      var X = this._internalRoot;
      if (X === null)
        throw new Error("Cannot update an unmounted root.");
      {
        if (typeof arguments[1] === "function")
          K("render(...): does not support the second callback argument. To execute a side effect after rendering, declare it in a component body with useEffect().");
        else if (B5(arguments[1]))
          K("You passed a container to the second argument of root.render(...). You don't need to pass it again since you already passed it to create the root.");
        else if (typeof arguments[1] !== "undefined")
          K("You passed a second argument to root.render(...) but it only accepts one argument.");
        var $ = X.containerInfo;
        if ($.nodeType !== f6) {
          var q = eO(X.current);
          if (q) {
            if (q.parentNode !== $)
              K("render(...): It looks like the React-rendered content of the root container was removed without using React. This is not supported and will cause errors. Instead, call root.unmount() to empty a root's container.");
          }
        }
      }
      F3(Z, X, null, null);
    }, j5.prototype.unmount = NN.prototype.unmount = function() {
      if (typeof arguments[0] === "function")
        K("unmount(...): does not support a callback argument. To execute a side effect after rendering, declare it in a component body with useEffect().");
      var Z = this._internalRoot;
      if (Z !== null) {
        this._internalRoot = null;
        var X = Z.containerInfo;
        if (SO())
          K("Attempted to synchronously unmount a root while React was already rendering. React cannot finish unmounting the root until the current render has completed, which may lead to a race condition.");
        U4(function() {
          F3(null, Z, null, null);
        }), UA(X);
      }
    };
    function ig(Z, X) {
      if (!B5(Z))
        throw new Error("createRoot(...): Target container is not a DOM element.");
      Lw(Z);
      var $ = !1, q = !1, H = "", G = Aw, E = null;
      if (X !== null && X !== void 0) {
        if (X.hydrate)
          W("hydrate through createRoot is deprecated. Use ReactDOMClient.hydrateRoot(container, <App />) instead.");
        else if (typeof X === "object" && X !== null && X.$$typeof === s8)
          K(`You passed a JSX element to createRoot. You probably meant to call root.render instead. Example usage:

  let root = createRoot(domContainer);
  root.render(<App />);`);
        if (X.unstable_strictMode === !0)
          $ = !0;
        if (X.identifierPrefix !== void 0)
          H = X.identifierPrefix;
        if (X.onRecoverableError !== void 0)
          G = X.onRecoverableError;
        if (X.transitionCallbacks !== void 0)
          E = X.transitionCallbacks;
      }
      var U = rO(Z, L9, null, $, q, H, G);
      z9(U.current, Z);
      var P = Z.nodeType === f6 ? Z.parentNode : Z;
      return wW(P), new NN(U);
    }
    function j5(Z) {
      this._internalRoot = Z;
    }
    function tg(Z) {
      if (Z)
        HC(Z);
    }
    j5.prototype.unstable_scheduleHydration = tg;
    function eg(Z, X, $) {
      if (!B5(Z))
        throw new Error("hydrateRoot(...): Target container is not a DOM element.");
      if (Lw(Z), X === void 0)
        K("Must provide initial children as second argument to hydrateRoot. Example usage: hydrateRoot(domContainer, <App />)");
      var q = $ != null ? $ : null, H = $ != null && $.hydratedSources || null, G = !1, E = !1, U = "", P = Aw;
      if ($ !== null && $ !== void 0) {
        if ($.unstable_strictMode === !0)
          G = !0;
        if ($.identifierPrefix !== void 0)
          U = $.identifierPrefix;
        if ($.onRecoverableError !== void 0)
          P = $.onRecoverableError;
      }
      var O = iO(X, null, Z, L9, q, G, E, U, P);
      if (z9(O.current, Z), wW(Z), H)
        for (var k = 0;k < H.length; k++) {
          var C = H[k];
          eI(O, C);
        }
      return new j5(O);
    }
    function B5(Z) {
      return !!(Z && (Z.nodeType === SQ || Z.nodeType === tX || Z.nodeType === A7 || !s1));
    }
    function U3(Z) {
      return !!(Z && (Z.nodeType === SQ || Z.nodeType === tX || Z.nodeType === A7 || Z.nodeType === f6 && Z.nodeValue === " react-mount-point-unstable "));
    }
    function Lw(Z) {
      {
        if (Z.nodeType === SQ && Z.tagName && Z.tagName.toUpperCase() === "BODY")
          K("createRoot(): Creating roots directly with document.body is discouraged, since its children are often manipulated by third-party scripts and browser extensions. This may lead to subtle reconciliation issues. Try using a container element created for your app.");
        if (_W(Z))
          if (Z._reactRootContainer)
            K("You are calling ReactDOMClient.createRoot() on a container that was previously passed to ReactDOM.render(). This is not supported.");
          else
            K("You are calling ReactDOMClient.createRoot() on a container that has already been passed to createRoot() before. Instead, call root.render() on the existing root instead if you want to update it.");
      }
    }
    var Qx = Q.ReactCurrentOwner, Ow;
    Ow = function(Z) {
      if (Z._reactRootContainer && Z.nodeType !== f6) {
        var X = eO(Z._reactRootContainer.current);
        if (X) {
          if (X.parentNode !== Z)
            K("render(...): It looks like the React-rendered content of this container was removed without using React. This is not supported and will cause errors. Instead, call ReactDOM.unmountComponentAtNode to empty a container.");
        }
      }
      var $ = !!Z._reactRootContainer, q = EN(Z), H = !!(q && l4(q));
      if (H && !$)
        K("render(...): Replacing React-rendered children with a new root component. If you intended to update the children of this node, you should instead have the existing children update their state and render the new components instead of calling ReactDOM.render.");
      if (Z.nodeType === SQ && Z.tagName && Z.tagName.toUpperCase() === "BODY")
        K("render(): Rendering components directly into document.body is discouraged, since its children are often manipulated by third-party scripts and browser extensions. This may lead to subtle reconciliation issues. Try rendering into a container element created for your app.");
    };
    function EN(Z) {
      if (!Z)
        return null;
      if (Z.nodeType === tX)
        return Z.documentElement;
      else
        return Z.firstChild;
    }
    function ww() {}
    function Zx(Z, X, $, q, H) {
      if (H) {
        if (typeof q === "function") {
          var G = q;
          q = function() {
            var B = R5(E);
            G.call(B);
          };
        }
        var E = iO(X, q, Z, s4, null, !1, !1, "", ww);
        Z._reactRootContainer = E, z9(E.current, Z);
        var U = Z.nodeType === f6 ? Z.parentNode : Z;
        return wW(U), U4(), E;
      } else {
        var P;
        while (P = Z.lastChild)
          Z.removeChild(P);
        if (typeof q === "function") {
          var O = q;
          q = function() {
            var B = R5(k);
            O.call(B);
          };
        }
        var k = rO(Z, s4, null, !1, !1, "", ww);
        Z._reactRootContainer = k, z9(k.current, Z);
        var C = Z.nodeType === f6 ? Z.parentNode : Z;
        return wW(C), U4(function() {
          F3(X, k, $, q);
        }), k;
      }
    }
    function Xx(Z, X) {
      if (Z !== null && typeof Z !== "function")
        K("%s(...): Expected the last optional `callback` argument to be a function. Instead received: %s.", X, Z);
    }
    function C5(Z, X, $, q, H) {
      Ow($), Xx(H === void 0 ? null : H, "render");
      var G = $._reactRootContainer, E;
      if (!G)
        E = Zx($, X, Z, H, q);
      else {
        if (E = G, typeof H === "function") {
          var U = H;
          H = function() {
            var P = R5(E);
            U.call(P);
          };
        }
        F3(X, E, Z, H);
      }
      return R5(E);
    }
    var Mw = !1;
    function Jx(Z) {
      {
        if (!Mw)
          Mw = !0, K("findDOMNode is deprecated and will be removed in the next major release. Instead, add a ref directly to the element you want to reference. Learn more about using refs safely here: https://reactjs.org/link/strict-mode-find-node");
        var X = Qx.current;
        if (X !== null && X.stateNode !== null) {
          var $ = X.stateNode._warnedAboutRefsInRender;
          if (!$)
            K("%s is accessing findDOMNode inside its render(). render() should be a pure function of props and state. It should never access something that requires stale data from the previous render, such as refs. Move this logic to componentDidMount and componentDidUpdate instead.", h0(X.type) || "A component");
          X.stateNode._warnedAboutRefsInRender = !0;
        }
      }
      if (Z == null)
        return null;
      if (Z.nodeType === SQ)
        return Z;
      return ug(Z, "findDOMNode");
    }
    function $x(Z, X, $) {
      if (K("ReactDOM.hydrate is no longer supported in React 18. Use hydrateRoot instead. Until you switch to the new API, your app will behave as if it's running React 17. Learn more: https://reactjs.org/link/switch-to-createroot"), !U3(X))
        throw new Error("Target container is not a DOM element.");
      {
        var q = _W(X) && X._reactRootContainer === void 0;
        if (q)
          K("You are calling ReactDOM.hydrate() on a container that was previously passed to ReactDOMClient.createRoot(). This is not supported. Did you mean to call hydrateRoot(container, element)?");
      }
      return C5(null, Z, X, !0, $);
    }
    function Yx(Z, X, $) {
      if (K("ReactDOM.render is no longer supported in React 18. Use createRoot instead. Until you switch to the new API, your app will behave as if it's running React 17. Learn more: https://reactjs.org/link/switch-to-createroot"), !U3(X))
        throw new Error("Target container is not a DOM element.");
      {
        var q = _W(X) && X._reactRootContainer === void 0;
        if (q)
          K("You are calling ReactDOM.render() on a container that was previously passed to ReactDOMClient.createRoot(). This is not supported. Did you mean to call root.render(element)?");
      }
      return C5(null, Z, X, !1, $);
    }
    function qx(Z, X, $, q) {
      if (K("ReactDOM.unstable_renderSubtreeIntoContainer() is no longer supported in React 18. Consider using a portal instead. Until you switch to the createRoot API, your app will behave as if it's running React 17. Learn more: https://reactjs.org/link/switch-to-createroot"), !U3($))
        throw new Error("Target container is not a DOM element.");
      if (Z == null || !aj(Z))
        throw new Error("parentComponent must be a valid React Component");
      return C5(Z, X, $, !1, q);
    }
    var Dw = !1;
    function Wx(Z) {
      if (!Dw)
        Dw = !0, K("unmountComponentAtNode is deprecated and will be removed in the next major release. Switch to the createRoot API. Learn more: https://reactjs.org/link/switch-to-createroot");
      if (!U3(Z))
        throw new Error("unmountComponentAtNode(...): Target container is not a DOM element.");
      {
        var X = _W(Z) && Z._reactRootContainer === void 0;
        if (X)
          K("You are calling ReactDOM.unmountComponentAtNode() on a container that was previously passed to ReactDOMClient.createRoot(). This is not supported. Did you mean to call root.unmount()?");
      }
      if (Z._reactRootContainer) {
        {
          var $ = EN(Z), q = $ && !l4($);
          if (q)
            K("unmountComponentAtNode(): The node you're attempting to unmount was rendered by another copy of React.");
        }
        return U4(function() {
          C5(null, null, Z, !1, function() {
            Z._reactRootContainer = null, UA(Z);
          });
        }), !0;
      } else {
        {
          var H = EN(Z), G = !!(H && l4(H)), E = Z.nodeType === SQ && U3(Z.parentNode) && !!Z.parentNode._reactRootContainer;
          if (G)
            K("unmountComponentAtNode(): The node you're attempting to unmount was rendered by React and is not a top-level container. %s", E ? "You may have accidentally passed in a React root node instead of its container." : "Instead, have the parent component update its state and rerender in order to remove this component.");
        }
        return !1;
      }
    }
    if (eB(cg), ZC(pg), XC(dg), JC(pZ), $C(rB), typeof Map !== "function" || Map.prototype == null || typeof Map.prototype.forEach !== "function" || typeof Set !== "function" || Set.prototype == null || typeof Set.prototype.clear !== "function" || typeof Set.prototype.forEach !== "function")
      K("React depends on Map and Set built-in types. Make sure that you load a polyfill in older browsers. https://reactjs.org/link/react-polyfills");
    fj(YS), uj(dz, eT, U4);
    function Kx(Z, X) {
      var $ = arguments.length > 2 && arguments[2] !== void 0 ? arguments[2] : null;
      if (!B5(X))
        throw new Error("Target container is not a DOM element.");
      return bg(Z, X, null, $);
    }
    function Hx(Z, X, $, q) {
      return qx(Z, X, $, q);
    }
    var FN = {
      usingClientEntryPoint: !1,
      Events: [l4, DY, N9, TU, gU, dz]
    };
    function Gx(Z, X) {
      if (!FN.usingClientEntryPoint)
        K('You are importing createRoot from "react-dom" which is not supported. You should instead import it from "react-dom/client".');
      return ig(Z, X);
    }
    function zx(Z, X, $) {
      if (!FN.usingClientEntryPoint)
        K('You are importing hydrateRoot from "react-dom" which is not supported. You should instead import it from "react-dom/client".');
      return eg(Z, X, $);
    }
    function Nx(Z) {
      if (SO())
        K("flushSync was called from inside a lifecycle method. React cannot flush when React is already rendering. Consider moving this call to a scheduler task or micro task.");
      return U4(Z);
    }
    var Ex = rg({
      findFiberByHostInstance: q$,
      bundleType: 1,
      version: WN,
      rendererPackageName: "react-dom"
    });
    if (!Ex && i1 && window.top === window.self) {
      if (navigator.userAgent.indexOf("Chrome") > -1 && navigator.userAgent.indexOf("Edge") === -1 || navigator.userAgent.indexOf("Firefox") > -1) {
        var kw = window.location.protocol;
        if (/^(https?|file):$/.test(kw))
          console.info("%cDownload the React DevTools for a better development experience: https://reactjs.org/link/react-devtools" + (kw === "file:" ? `
You might need to use a local HTTP server (instead of file://): https://reactjs.org/link/react-devtools-faq` : ""), "font-weight:bold");
      }
    }
    if (Dx.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED = FN, Dx.createPortal = Kx, Dx.createRoot = Gx, Dx.findDOMNode = Jx, Dx.flushSync = Nx, Dx.hydrate = $x, Dx.hydrateRoot = zx, Dx.render = Yx, Dx.unmountComponentAtNode = Wx, Dx.unstable_batchedUpdates = dz, Dx.unstable_renderSubtreeIntoContainer = Hx, Dx.version = WN, typeof __REACT_DEVTOOLS_GLOBAL_HOOK__ !== "undefined" && typeof __REACT_DEVTOOLS_GLOBAL_HOOK__.registerInternalModuleStop === "function")
      __REACT_DEVTOOLS_GLOBAL_HOOK__.registerInternalModuleStop(new Error);
  })();
});

// node_modules/react-dom/index.js
var PN = $6((uu, Bw) => {
  var kx = D6(jw(), 1);
  Bw.exports = kx;
});

// node_modules/react-dom/client.js
var Cw = $6((Rx) => {
  var aY = D6(PN(), 1);
  oY = aY.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED, Rx.createRoot = function(Q, J) {
    oY.usingClientEntryPoint = !0;
    try {
      return aY.createRoot(Q, J);
    } finally {
      oY.usingClientEntryPoint = !1;
    }
  }, Rx.hydrateRoot = function(Q, J, Y) {
    oY.usingClientEntryPoint = !0;
    try {
      return aY.hydrateRoot(Q, J, Y);
    } finally {
      oY.usingClientEntryPoint = !1;
    }
  };
  var oY;
});

// node_modules/react-is/cjs/react-is.development.js
var Vw = $6((jx) => {
  (function() {
    var Q = typeof Symbol === "function" && Symbol.for, J = Q ? Symbol.for("react.element") : 60103, Y = Q ? Symbol.for("react.portal") : 60106, W = Q ? Symbol.for("react.fragment") : 60107, K = Q ? Symbol.for("react.strict_mode") : 60108, z = Q ? Symbol.for("react.profiler") : 60114, N = Q ? Symbol.for("react.provider") : 60109, F = Q ? Symbol.for("react.context") : 60110, L = Q ? Symbol.for("react.async_mode") : 60111, w = Q ? Symbol.for("react.concurrent_mode") : 60111, D = Q ? Symbol.for("react.forward_ref") : 60112, R = Q ? Symbol.for("react.suspense") : 60113, V = Q ? Symbol.for("react.suspense_list") : 60120, g = Q ? Symbol.for("react.memo") : 60115, s = Q ? Symbol.for("react.lazy") : 60116, i = Q ? Symbol.for("react.block") : 60121, F0 = Q ? Symbol.for("react.fundamental") : 60117, r = Q ? Symbol.for("react.responder") : 60118, J0 = Q ? Symbol.for("react.scope") : 60119;
    function l(Z0) {
      return typeof Z0 === "string" || typeof Z0 === "function" || Z0 === W || Z0 === w || Z0 === z || Z0 === K || Z0 === R || Z0 === V || typeof Z0 === "object" && Z0 !== null && (Z0.$$typeof === s || Z0.$$typeof === g || Z0.$$typeof === N || Z0.$$typeof === F || Z0.$$typeof === D || Z0.$$typeof === F0 || Z0.$$typeof === r || Z0.$$typeof === J0 || Z0.$$typeof === i);
    }
    function t(Z0) {
      if (typeof Z0 === "object" && Z0 !== null) {
        var F6 = Z0.$$typeof;
        switch (F6) {
          case J:
            var C1 = Z0.type;
            switch (C1) {
              case L:
              case w:
              case W:
              case z:
              case K:
              case R:
                return C1;
              default:
                var v1 = C1 && C1.$$typeof;
                switch (v1) {
                  case F:
                  case D:
                  case s:
                  case g:
                  case N:
                    return v1;
                  default:
                    return F6;
                }
            }
          case Y:
            return F6;
        }
      }
      return;
    }
    var $0 = L, M0 = w, c0 = F, I0 = N, p = J, o = D, Y0 = W, A0 = s, P0 = g, Y1 = Y, N0 = z, W0 = K, v0 = R, n1 = !1;
    function g1(Z0) {
      if (!n1)
        n1 = !0, console.warn("The ReactIs.isAsyncMode() alias has been deprecated, and will be removed in React 17+. Update your code to use ReactIs.isConcurrentMode() instead. It has the exact same API.");
      return s1(Z0) || t(Z0) === L;
    }
    function s1(Z0) {
      return t(Z0) === w;
    }
    function _1(Z0) {
      return t(Z0) === F;
    }
    function U1(Z0) {
      return t(Z0) === N;
    }
    function x0(Z0) {
      return typeof Z0 === "object" && Z0 !== null && Z0.$$typeof === J;
    }
    function N6(Z0) {
      return t(Z0) === D;
    }
    function C6(Z0) {
      return t(Z0) === W;
    }
    function o1(Z0) {
      return t(Z0) === s;
    }
    function f1(Z0) {
      return t(Z0) === g;
    }
    function E6(Z0) {
      return t(Z0) === Y;
    }
    function x1(Z0) {
      return t(Z0) === z;
    }
    function l0(Z0) {
      return t(Z0) === K;
    }
    function i1(Z0) {
      return t(Z0) === R;
    }
    jx.AsyncMode = $0, jx.ConcurrentMode = M0, jx.ContextConsumer = c0, jx.ContextProvider = I0, jx.Element = p, jx.ForwardRef = o, jx.Fragment = Y0, jx.Lazy = A0, jx.Memo = P0, jx.Portal = Y1, jx.Profiler = N0, jx.StrictMode = W0, jx.Suspense = v0, jx.isAsyncMode = g1, jx.isConcurrentMode = s1, jx.isContextConsumer = _1, jx.isContextProvider = U1, jx.isElement = x0, jx.isForwardRef = N6, jx.isFragment = C6, jx.isLazy = o1, jx.isMemo = f1, jx.isPortal = E6, jx.isProfiler = x1, jx.isStrictMode = l0, jx.isSuspense = i1, jx.isValidElementType = l, jx.typeOf = t;
  })();
});

// node_modules/hoist-non-react-statics/dist/hoist-non-react-statics.cjs.js
var vw = $6((wc, xw) => {
  var rY = D6(Vw(), 1), Bx = {
    childContextTypes: !0,
    contextType: !0,
    contextTypes: !0,
    defaultProps: !0,
    displayName: !0,
    getDefaultProps: !0,
    getDerivedStateFromError: !0,
    getDerivedStateFromProps: !0,
    mixins: !0,
    propTypes: !0,
    type: !0
  }, Cx = {
    name: !0,
    length: !0,
    prototype: !0,
    caller: !0,
    callee: !0,
    arguments: !0,
    arity: !0
  }, Vx = {
    $$typeof: !0,
    render: !0,
    defaultProps: !0,
    displayName: !0,
    propTypes: !0
  }, Tw = {
    $$typeof: !0,
    compare: !0,
    defaultProps: !0,
    displayName: !0,
    propTypes: !0,
    type: !0
  }, AN = {};
  AN[rY.ForwardRef] = Vx;
  AN[rY.Memo] = Tw;
  function Sw(Q) {
    if (rY.isMemo(Q))
      return Tw;
    return AN[Q.$$typeof] || Bx;
  }
  var { defineProperty: Sx, getOwnPropertyNames: Ix, getOwnPropertySymbols: Iw, getOwnPropertyDescriptor: _x, getPrototypeOf: Tx, prototype: _w } = Object;
  function gw(Q, J, Y) {
    if (typeof J !== "string") {
      if (_w) {
        var W = Tx(J);
        if (W && W !== _w)
          gw(Q, W, Y);
      }
      var K = Ix(J);
      if (Iw)
        K = K.concat(Iw(J));
      var z = Sw(Q), N = Sw(J);
      for (var F = 0;F < K.length; ++F) {
        var L = K[F];
        if (!Cx[L] && !(Y && Y[L]) && !(N && N[L]) && !(z && z[L])) {
          var w = _x(J, L);
          try {
            Sx(Q, L, w);
          } catch (D) {}
        }
      }
    }
    return Q;
  }
  xw.exports = gw;
});

// node_modules/object-assign/index.js
var fw = $6((Mc, yw) => {
  var hw = Object.getOwnPropertySymbols, gx = Object.prototype.hasOwnProperty, xx = Object.prototype.propertyIsEnumerable;
  function vx(Q) {
    if (Q === null || Q === void 0)
      throw new TypeError("Object.assign cannot be called with null or undefined");
    return Object(Q);
  }
  function hx() {
    try {
      if (!Object.assign)
        return !1;
      var Q = new String("abc");
      if (Q[5] = "de", Object.getOwnPropertyNames(Q)[0] === "5")
        return !1;
      var J = {};
      for (var Y = 0;Y < 10; Y++)
        J["_" + String.fromCharCode(Y)] = Y;
      var W = Object.getOwnPropertyNames(J).map(function(z) {
        return J[z];
      });
      if (W.join("") !== "0123456789")
        return !1;
      var K = {};
      if ("abcdefghijklmnopqrst".split("").forEach(function(z) {
        K[z] = z;
      }), Object.keys(Object.assign({}, K)).join("") !== "abcdefghijklmnopqrst")
        return !1;
      return !0;
    } catch (z) {
      return !1;
    }
  }
  yw.exports = hx() ? Object.assign : function(Q, J) {
    var Y, W = vx(Q), K;
    for (var z = 1;z < arguments.length; z++) {
      Y = Object(arguments[z]);
      for (var N in Y)
        if (gx.call(Y, N))
          W[N] = Y[N];
      if (hw) {
        K = hw(Y);
        for (var F = 0;F < K.length; F++)
          if (xx.call(Y, K[F]))
            W[K[F]] = Y[K[F]];
      }
    }
    return W;
  };
});

// node_modules/prop-types/lib/ReactPropTypesSecret.js
var bw = $6((Dc, mw) => {
  var yx = "SECRET_DO_NOT_PASS_THIS_OR_YOU_WILL_BE_FIRED";
  mw.exports = yx;
});

// node_modules/prop-types/lib/has.js
var cw = $6((kc, uw) => {
  uw.exports = Function.call.bind(Object.prototype.hasOwnProperty);
});

// node_modules/prop-types/checkPropTypes.js
var lw = $6((Rc, dw) => {
  var LN = function() {};
  ON = bw(), L3 = {}, wN = cw(), LN = function(Q) {
    var J = "Warning: " + Q;
    if (typeof console !== "undefined")
      console.error(J);
    try {
      throw new Error(J);
    } catch (Y) {}
  };
  var ON, L3, wN;
  function pw(Q, J, Y, W, K) {
    for (var z in Q)
      if (wN(Q, z)) {
        var N;
        try {
          if (typeof Q[z] !== "function") {
            var F = Error((W || "React class") + ": " + Y + " type `" + z + "` is invalid; it must be a function, usually from the `prop-types` package, but received `" + typeof Q[z] + "`.This often happens because of typos such as `PropTypes.function` instead of `PropTypes.func`.");
            throw F.name = "Invariant Violation", F;
          }
          N = Q[z](J, z, W, Y, null, ON);
        } catch (w) {
          N = w;
        }
        if (N && !(N instanceof Error))
          LN((W || "React class") + ": type specification of " + Y + " `" + z + "` is invalid; the type checker function must return `null` or an `Error` but returned a " + typeof N + ". You may have forgotten to pass an argument to the type checker creator (arrayOf, instanceOf, objectOf, oneOf, oneOfType, and shape all require an argument).");
        if (N instanceof Error && !(N.message in L3)) {
          L3[N.message] = !0;
          var L = K ? K() : "";
          LN("Failed " + Y + " type: " + N.message + (L != null ? L : ""));
        }
      }
  }
  pw.resetWarningCache = function() {
    L3 = {};
  };
  dw.exports = pw;
});

// node_modules/streamlit-component-lib/node_modules/react/cjs/react.development.js
var nw = $6((fx) => {
  (function() {
    var Q = fw(), J = lw(), Y = "16.14.0", W = typeof Symbol === "function" && Symbol.for, K = W ? Symbol.for("react.element") : 60103, z = W ? Symbol.for("react.portal") : 60106, N = W ? Symbol.for("react.fragment") : 60107, F = W ? Symbol.for("react.strict_mode") : 60108, L = W ? Symbol.for("react.profiler") : 60114, w = W ? Symbol.for("react.provider") : 60109, D = W ? Symbol.for("react.context") : 60110, R = W ? Symbol.for("react.concurrent_mode") : 60111, V = W ? Symbol.for("react.forward_ref") : 60112, g = W ? Symbol.for("react.suspense") : 60113, s = W ? Symbol.for("react.suspense_list") : 60120, i = W ? Symbol.for("react.memo") : 60115, F0 = W ? Symbol.for("react.lazy") : 60116, r = W ? Symbol.for("react.block") : 60121, J0 = W ? Symbol.for("react.fundamental") : 60117, l = W ? Symbol.for("react.responder") : 60118, t = W ? Symbol.for("react.scope") : 60119, $0 = typeof Symbol === "function" && Symbol.iterator, M0 = "@@iterator";
    function c0(M) {
      if (M === null || typeof M !== "object")
        return null;
      var S = $0 && M[$0] || M[M0];
      if (typeof S === "function")
        return S;
      return null;
    }
    var I0 = {
      current: null
    }, p = {
      suspense: null
    }, o = {
      current: null
    }, Y0 = /^(.*)[\\\/]/;
    function A0(M, S, y) {
      var d = "";
      if (S) {
        var K0 = S.fileName, H1 = K0.replace(Y0, "");
        if (/^index\./.test(H1)) {
          var _0 = K0.match(Y0);
          if (_0) {
            var d0 = _0[1];
            if (d0) {
              var O6 = d0.replace(Y0, "");
              H1 = O6 + "/" + H1;
            }
          }
        }
        d = " (at " + H1 + ":" + S.lineNumber + ")";
      } else if (y)
        d = " (created by " + y + ")";
      return `
    in ` + (M || "Unknown") + d;
    }
    var P0 = 1;
    function Y1(M) {
      return M._status === P0 ? M._result : null;
    }
    function N0(M, S, y) {
      var d = S.displayName || S.name || "";
      return M.displayName || (d !== "" ? y + "(" + d + ")" : y);
    }
    function W0(M) {
      if (M == null)
        return null;
      if (typeof M.tag === "number")
        x0("Received an unexpected object in getComponentName(). This is likely a bug in React. Please file an issue.");
      if (typeof M === "function")
        return M.displayName || M.name || null;
      if (typeof M === "string")
        return M;
      switch (M) {
        case N:
          return "Fragment";
        case z:
          return "Portal";
        case L:
          return "Profiler";
        case F:
          return "StrictMode";
        case g:
          return "Suspense";
        case s:
          return "SuspenseList";
      }
      if (typeof M === "object")
        switch (M.$$typeof) {
          case D:
            return "Context.Consumer";
          case w:
            return "Context.Provider";
          case V:
            return N0(M, M.render, "ForwardRef");
          case i:
            return W0(M.type);
          case r:
            return W0(M.render);
          case F0: {
            var S = M, y = Y1(S);
            if (y)
              return W0(y);
            break;
          }
        }
      return null;
    }
    var v0 = {}, n1 = null;
    function g1(M) {
      n1 = M;
    }
    v0.getCurrentStack = null, v0.getStackAddendum = function() {
      var M = "";
      if (n1) {
        var S = W0(n1.type), y = n1._owner;
        M += A0(S, n1._source, y && W0(y.type));
      }
      var d = v0.getCurrentStack;
      if (d)
        M += d() || "";
      return M;
    };
    var s1 = {
      current: !1
    }, _1 = {
      ReactCurrentDispatcher: I0,
      ReactCurrentBatchConfig: p,
      ReactCurrentOwner: o,
      IsSomeRendererActing: s1,
      assign: Q
    };
    Q(_1, {
      ReactDebugCurrentFrame: v0,
      ReactComponentTreeHook: {}
    });
    function U1(M) {
      {
        for (var S = arguments.length, y = new Array(S > 1 ? S - 1 : 0), d = 1;d < S; d++)
          y[d - 1] = arguments[d];
        N6("warn", M, y);
      }
    }
    function x0(M) {
      {
        for (var S = arguments.length, y = new Array(S > 1 ? S - 1 : 0), d = 1;d < S; d++)
          y[d - 1] = arguments[d];
        N6("error", M, y);
      }
    }
    function N6(M, S, y) {
      {
        var d = y.length > 0 && typeof y[y.length - 1] === "string" && y[y.length - 1].indexOf(`
    in`) === 0;
        if (!d) {
          var K0 = _1.ReactDebugCurrentFrame, H1 = K0.getStackAddendum();
          if (H1 !== "")
            S += "%s", y = y.concat([H1]);
        }
        var _0 = y.map(function(h0) {
          return "" + h0;
        });
        _0.unshift("Warning: " + S), Function.prototype.apply.call(console[M], console, _0);
        try {
          var d0 = 0, O6 = "Warning: " + S.replace(/%s/g, function() {
            return y[d0++];
          });
          throw new Error(O6);
        } catch (h0) {}
      }
    }
    var C6 = {};
    function o1(M, S) {
      {
        var y = M.constructor, d = y && (y.displayName || y.name) || "ReactClass", K0 = d + "." + S;
        if (C6[K0])
          return;
        x0("Can't call %s on a component that is not yet mounted. This is a no-op, but it might indicate a bug in your application. Instead, assign to `this.state` directly or define a `state = {};` class property with the desired state in the %s component.", S, d), C6[K0] = !0;
      }
    }
    var f1 = {
      isMounted: function(M) {
        return !1;
      },
      enqueueForceUpdate: function(M, S, y) {
        o1(M, "forceUpdate");
      },
      enqueueReplaceState: function(M, S, y, d) {
        o1(M, "replaceState");
      },
      enqueueSetState: function(M, S, y, d) {
        o1(M, "setState");
      }
    }, E6 = {};
    Object.freeze(E6);
    function x1(M, S, y) {
      this.props = M, this.context = S, this.refs = E6, this.updater = y || f1;
    }
    x1.prototype.isReactComponent = {}, x1.prototype.setState = function(M, S) {
      if (!(typeof M === "object" || typeof M === "function" || M == null))
        throw Error("setState(...): takes an object of state variables to update or a function which returns an object of state variables.");
      this.updater.enqueueSetState(this, M, S, "setState");
    }, x1.prototype.forceUpdate = function(M) {
      this.updater.enqueueForceUpdate(this, M, "forceUpdate");
    };
    {
      var l0 = {
        isMounted: ["isMounted", "Instead, make sure to clean up subscriptions and pending requests in componentWillUnmount to prevent memory leaks."],
        replaceState: ["replaceState", "Refactor your code to use setState instead (see https://github.com/facebook/react/issues/3236)."]
      }, i1 = function(M, S) {
        Object.defineProperty(x1.prototype, M, {
          get: function() {
            U1("%s(...) is deprecated in plain JavaScript React classes. %s", S[0], S[1]);
            return;
          }
        });
      };
      for (var Z0 in l0)
        if (l0.hasOwnProperty(Z0))
          i1(Z0, l0[Z0]);
    }
    function F6() {}
    F6.prototype = x1.prototype;
    function C1(M, S, y) {
      this.props = M, this.context = S, this.refs = E6, this.updater = y || f1;
    }
    var v1 = C1.prototype = new F6;
    v1.constructor = C1, Q(v1, x1.prototype), v1.isPureReactComponent = !0;
    function h6() {
      var M = {
        current: null
      };
      return Object.seal(M), M;
    }
    var c8 = Object.prototype.hasOwnProperty, p6 = {
      key: !0,
      ref: !0,
      __self: !0,
      __source: !0
    }, k8, q8, W8;
    W8 = {};
    function d6(M) {
      if (c8.call(M, "ref")) {
        var S = Object.getOwnPropertyDescriptor(M, "ref").get;
        if (S && S.isReactWarning)
          return !1;
      }
      return M.ref !== void 0;
    }
    function A6(M) {
      if (c8.call(M, "key")) {
        var S = Object.getOwnPropertyDescriptor(M, "key").get;
        if (S && S.isReactWarning)
          return !1;
      }
      return M.key !== void 0;
    }
    function RQ(M, S) {
      var y = function() {
        if (!k8)
          k8 = !0, x0("%s: `key` is not a prop. Trying to access it will result in `undefined` being returned. If you need to access the same value within the child component, you should pass it as a different prop. (https://fb.me/react-special-props)", S);
      };
      y.isReactWarning = !0, Object.defineProperty(M, "key", {
        get: y,
        configurable: !0
      });
    }
    function R8(M, S) {
      var y = function() {
        if (!q8)
          q8 = !0, x0("%s: `ref` is not a prop. Trying to access it will result in `undefined` being returned. If you need to access the same value within the child component, you should pass it as a different prop. (https://fb.me/react-special-props)", S);
      };
      y.isReactWarning = !0, Object.defineProperty(M, "ref", {
        get: y,
        configurable: !0
      });
    }
    function WQ(M) {
      if (typeof M.ref === "string" && o.current && M.__self && o.current.stateNode !== M.__self) {
        var S = W0(o.current.type);
        if (!W8[S])
          x0('Component "%s" contains the string ref "%s". Support for string refs will be removed in a future major release. This case cannot be automatically converted to an arrow function. We ask you to manually fix this case by using useRef() or createRef() instead. Learn more about using refs safely here: https://fb.me/react-strict-mode-string-ref', W0(o.current.type), M.ref), W8[S] = !0;
      }
    }
    var l6 = function(M, S, y, d, K0, H1, _0) {
      var d0 = {
        $$typeof: K,
        type: M,
        key: S,
        ref: y,
        props: _0,
        _owner: H1
      };
      if (d0._store = {}, Object.defineProperty(d0._store, "validated", {
        configurable: !1,
        enumerable: !1,
        writable: !0,
        value: !1
      }), Object.defineProperty(d0, "_self", {
        configurable: !1,
        enumerable: !1,
        writable: !1,
        value: d
      }), Object.defineProperty(d0, "_source", {
        configurable: !1,
        enumerable: !1,
        writable: !1,
        value: K0
      }), Object.freeze)
        Object.freeze(d0.props), Object.freeze(d0);
      return d0;
    };
    function p8(M, S, y) {
      var d, K0 = {}, H1 = null, _0 = null, d0 = null, O6 = null;
      if (S != null) {
        if (d6(S))
          _0 = S.ref, WQ(S);
        if (A6(S))
          H1 = "" + S.key;
        d0 = S.__self === void 0 ? null : S.__self, O6 = S.__source === void 0 ? null : S.__source;
        for (d in S)
          if (c8.call(S, d) && !p6.hasOwnProperty(d))
            K0[d] = S[d];
      }
      var h0 = arguments.length - 2;
      if (h0 === 1)
        K0.children = y;
      else if (h0 > 1) {
        var B8 = Array(h0);
        for (var s6 = 0;s6 < h0; s6++)
          B8[s6] = arguments[s6 + 2];
        if (Object.freeze)
          Object.freeze(B8);
        K0.children = B8;
      }
      if (M && M.defaultProps) {
        var V0 = M.defaultProps;
        for (d in V0)
          if (K0[d] === void 0)
            K0[d] = V0[d];
      }
      if (H1 || _0) {
        var GQ = typeof M === "function" ? M.displayName || M.name || "Unknown" : M;
        if (H1)
          RQ(K0, GQ);
        if (_0)
          R8(K0, GQ);
      }
      return l6(M, H1, _0, d0, O6, o.current, K0);
    }
    function d8(M, S) {
      var y = l6(M.type, S, M.ref, M._self, M._source, M._owner, M.props);
      return y;
    }
    function jQ(M, S, y) {
      if (M === null || M === void 0)
        throw Error("React.cloneElement(...): The argument must be a React element, but you passed " + M + ".");
      var d, K0 = Q({}, M.props), H1 = M.key, _0 = M.ref, d0 = M._self, O6 = M._source, h0 = M._owner;
      if (S != null) {
        if (d6(S))
          _0 = S.ref, h0 = o.current;
        if (A6(S))
          H1 = "" + S.key;
        var B8;
        if (M.type && M.type.defaultProps)
          B8 = M.type.defaultProps;
        for (d in S)
          if (c8.call(S, d) && !p6.hasOwnProperty(d))
            if (S[d] === void 0 && B8 !== void 0)
              K0[d] = B8[d];
            else
              K0[d] = S[d];
      }
      var s6 = arguments.length - 2;
      if (s6 === 1)
        K0.children = y;
      else if (s6 > 1) {
        var V0 = Array(s6);
        for (var GQ = 0;GQ < s6; GQ++)
          V0[GQ] = arguments[GQ + 2];
        K0.children = V0;
      }
      return l6(M.type, H1, _0, d0, O6, h0, K0);
    }
    function Q0(M) {
      return typeof M === "object" && M !== null && M.$$typeof === K;
    }
    var D0 = ".", f0 = ":";
    function k1(M) {
      var S = /[=:]/g, y = {
        "=": "=0",
        ":": "=2"
      }, d = ("" + M).replace(S, function(K0) {
        return y[K0];
      });
      return "$" + d;
    }
    var h1 = !1, V6 = /\/+/g;
    function a1(M) {
      return ("" + M).replace(V6, "$&/");
    }
    var l8 = 10, W1 = [];
    function y1(M, S, y, d) {
      if (W1.length) {
        var K0 = W1.pop();
        return K0.result = M, K0.keyPrefix = S, K0.func = y, K0.context = d, K0.count = 0, K0;
      } else
        return {
          result: M,
          keyPrefix: S,
          func: y,
          context: d,
          count: 0
        };
    }
    function t1(M) {
      if (M.result = null, M.keyPrefix = null, M.func = null, M.context = null, M.count = 0, W1.length < l8)
        W1.push(M);
    }
    function X6(M, S, y, d) {
      var K0 = typeof M;
      if (K0 === "undefined" || K0 === "boolean")
        M = null;
      var H1 = !1;
      if (M === null)
        H1 = !0;
      else
        switch (K0) {
          case "string":
          case "number":
            H1 = !0;
            break;
          case "object":
            switch (M.$$typeof) {
              case K:
              case z:
                H1 = !0;
            }
        }
      if (H1)
        return y(d, M, S === "" ? D0 + n8(M, 0) : S), 1;
      var _0, d0, O6 = 0, h0 = S === "" ? D0 : S + f0;
      if (Array.isArray(M))
        for (var B8 = 0;B8 < M.length; B8++)
          _0 = M[B8], d0 = h0 + n8(_0, B8), O6 += X6(_0, d0, y, d);
      else {
        var s6 = c0(M);
        if (typeof s6 === "function") {
          if (s6 === M.entries) {
            if (!h1)
              U1("Using Maps as children is deprecated and will be removed in a future major release. Consider converting children to an array of keyed ReactElements instead.");
            h1 = !0;
          }
          var V0 = s6.call(M), GQ, z8 = 0;
          while (!(GQ = V0.next()).done)
            _0 = GQ.value, d0 = h0 + n8(_0, z8++), O6 += X6(_0, d0, y, d);
        } else if (K0 === "object") {
          var MX = "";
          MX = " If you meant to render a collection of children, use an array instead." + v0.getStackAddendum();
          var bZ = "" + M;
          throw Error("Objects are not valid as a React child (found: " + (bZ === "[object Object]" ? "object with keys {" + Object.keys(M).join(", ") + "}" : bZ) + ")." + MX);
        }
      }
      return O6;
    }
    function L6(M, S, y) {
      if (M == null)
        return 0;
      return X6(M, "", S, y);
    }
    function n8(M, S) {
      if (typeof M === "object" && M !== null && M.key != null)
        return k1(M.key);
      return S.toString(36);
    }
    function K8(M, S, y) {
      var { func: d, context: K0 } = M;
      d.call(K0, S, M.count++);
    }
    function H8(M, S, y) {
      if (M == null)
        return M;
      var d = y1(null, null, S, y);
      L6(M, K8, d), t1(d);
    }
    function j8(M, S, y) {
      var { result: d, keyPrefix: K0, func: H1, context: _0 } = M, d0 = H1.call(_0, S, M.count++);
      if (Array.isArray(d0))
        G8(d0, d, y, function(O6) {
          return O6;
        });
      else if (d0 != null) {
        if (Q0(d0))
          d0 = d8(d0, K0 + (d0.key && (!S || S.key !== d0.key) ? a1(d0.key) + "/" : "") + y);
        d.push(d0);
      }
    }
    function G8(M, S, y, d, K0) {
      var H1 = "";
      if (y != null)
        H1 = a1(y) + "/";
      var _0 = y1(S, H1, d, K0);
      L6(M, j8, _0), t1(_0);
    }
    function y6(M, S, y) {
      if (M == null)
        return M;
      var d = [];
      return G8(M, d, null, S, y), d;
    }
    function BQ(M) {
      return L6(M, function() {
        return null;
      }, null);
    }
    function s8(M) {
      var S = [];
      return G8(M, S, null, function(y) {
        return y;
      }), S;
    }
    function o8(M) {
      if (!Q0(M))
        throw Error("React.Children.only expected to receive a single React element child.");
      return M;
    }
    function KQ(M, S) {
      if (S === void 0)
        S = null;
      else if (S !== null && typeof S !== "function")
        x0("createContext: Expected the optional second argument to be a function. Instead received: %s", S);
      var y = {
        $$typeof: D,
        _calculateChangedBits: S,
        _currentValue: M,
        _currentValue2: M,
        _threadCount: 0,
        Provider: null,
        Consumer: null
      };
      y.Provider = {
        $$typeof: w,
        _context: y
      };
      var d = !1, K0 = !1;
      {
        var H1 = {
          $$typeof: D,
          _context: y,
          _calculateChangedBits: y._calculateChangedBits
        };
        Object.defineProperties(H1, {
          Provider: {
            get: function() {
              if (!K0)
                K0 = !0, x0("Rendering <Context.Consumer.Provider> is not supported and will be removed in a future major release. Did you mean to render <Context.Provider> instead?");
              return y.Provider;
            },
            set: function(_0) {
              y.Provider = _0;
            }
          },
          _currentValue: {
            get: function() {
              return y._currentValue;
            },
            set: function(_0) {
              y._currentValue = _0;
            }
          },
          _currentValue2: {
            get: function() {
              return y._currentValue2;
            },
            set: function(_0) {
              y._currentValue2 = _0;
            }
          },
          _threadCount: {
            get: function() {
              return y._threadCount;
            },
            set: function(_0) {
              y._threadCount = _0;
            }
          },
          Consumer: {
            get: function() {
              if (!d)
                d = !0, x0("Rendering <Context.Consumer.Consumer> is not supported and will be removed in a future major release. Did you mean to render <Context.Consumer> instead?");
              return y.Consumer;
            }
          }
        }), y.Consumer = H1;
      }
      return y._currentRenderer = null, y._currentRenderer2 = null, y;
    }
    function PX(M) {
      var S = {
        $$typeof: F0,
        _ctor: M,
        _status: -1,
        _result: null
      };
      {
        var y, d;
        Object.defineProperties(S, {
          defaultProps: {
            configurable: !0,
            get: function() {
              return y;
            },
            set: function(K0) {
              x0("React.lazy(...): It is not supported to assign `defaultProps` to a lazy component import. Either specify them where the component is defined, or create a wrapping component around it."), y = K0, Object.defineProperty(S, "defaultProps", {
                enumerable: !0
              });
            }
          },
          propTypes: {
            configurable: !0,
            get: function() {
              return d;
            },
            set: function(K0) {
              x0("React.lazy(...): It is not supported to assign `propTypes` to a lazy component import. Either specify them where the component is defined, or create a wrapping component around it."), d = K0, Object.defineProperty(S, "propTypes", {
                enumerable: !0
              });
            }
          }
        });
      }
      return S;
    }
    function pQ(M) {
      {
        if (M != null && M.$$typeof === i)
          x0("forwardRef requires a render function but received a `memo` component. Instead of forwardRef(memo(...)), use memo(forwardRef(...)).");
        else if (typeof M !== "function")
          x0("forwardRef requires a render function but was given %s.", M === null ? "null" : typeof M);
        else if (M.length !== 0 && M.length !== 2)
          x0("forwardRef render functions accept exactly two parameters: props and ref. %s", M.length === 1 ? "Did you forget to use the ref parameter?" : "Any additional parameter will be undefined.");
        if (M != null) {
          if (M.defaultProps != null || M.propTypes != null)
            x0("forwardRef render functions do not support propTypes or defaultProps. Did you accidentally pass a React component?");
        }
      }
      return {
        $$typeof: V,
        render: M
      };
    }
    function HQ(M) {
      return typeof M === "string" || typeof M === "function" || M === N || M === R || M === L || M === F || M === g || M === s || typeof M === "object" && M !== null && (M.$$typeof === F0 || M.$$typeof === i || M.$$typeof === w || M.$$typeof === D || M.$$typeof === V || M.$$typeof === J0 || M.$$typeof === l || M.$$typeof === t || M.$$typeof === r);
    }
    function fZ(M, S) {
      if (!HQ(M))
        x0("memo: The first argument must be a component. Instead received: %s", M === null ? "null" : typeof M);
      return {
        $$typeof: i,
        type: M,
        compare: S === void 0 ? null : S
      };
    }
    function V1() {
      var M = I0.current;
      if (M === null)
        throw Error(`Invalid hook call. Hooks can only be called inside of the body of a function component. This could happen for one of the following reasons:
1. You might have mismatching versions of React and the renderer (such as React DOM)
2. You might be breaking the Rules of Hooks
3. You might have more than one copy of React in the same app
See https://fb.me/react-invalid-hook-call for tips about how to debug and fix this problem.`);
      return M;
    }
    function V4(M, S) {
      var y = V1();
      {
        if (S !== void 0)
          x0("useContext() second argument is reserved for future use in React. Passing it is not supported. You passed: %s.%s", S, typeof S === "number" && Array.isArray(arguments[2]) ? `

Did you call array.map(useContext)? Calling Hooks inside a loop is not supported. Learn more at https://fb.me/rules-of-hooks` : "");
        if (M._context !== void 0) {
          var d = M._context;
          if (d.Consumer === M)
            x0("Calling useContext(Context.Consumer) is not supported, may cause bugs, and will be removed in a future major release. Did you mean to call useContext(Context) instead?");
          else if (d.Provider === M)
            x0("Calling useContext(Context.Provider) is not supported. Did you mean to call useContext(Context) instead?");
        }
      }
      return y.useContext(M, S);
    }
    function S4(M) {
      var S = V1();
      return S.useState(M);
    }
    function nX(M, S, y) {
      var d = V1();
      return d.useReducer(M, S, y);
    }
    function n6(M) {
      var S = V1();
      return S.useRef(M);
    }
    function xq(M, S) {
      var y = V1();
      return y.useEffect(M, S);
    }
    function vq(M, S) {
      var y = V1();
      return y.useLayoutEffect(M, S);
    }
    function s$(M, S) {
      var y = V1();
      return y.useCallback(M, S);
    }
    function hq(M, S) {
      var y = V1();
      return y.useMemo(M, S);
    }
    function yq(M, S, y) {
      var d = V1();
      return d.useImperativeHandle(M, S, y);
    }
    function fq(M, S) {
      {
        var y = V1();
        return y.useDebugValue(M, S);
      }
    }
    var bJ = !1;
    function o$() {
      if (o.current) {
        var M = W0(o.current.type);
        if (M)
          return `

Check the render method of \`` + M + "`.";
      }
      return "";
    }
    function mZ(M) {
      if (M !== void 0) {
        var S = M.fileName.replace(/^.*[\\\/]/, ""), y = M.lineNumber;
        return `

Check your code at ` + S + ":" + y + ".";
      }
      return "";
    }
    function K1(M) {
      if (M !== null && M !== void 0)
        return mZ(M.__source);
      return "";
    }
    var AX = {};
    function LX(M) {
      var S = o$();
      if (!S) {
        var y = typeof M === "string" ? M : M.displayName || M.name;
        if (y)
          S = `

Check the top-level render call using <` + y + ">.";
      }
      return S;
    }
    function I4(M, S) {
      if (!M._store || M._store.validated || M.key != null)
        return;
      M._store.validated = !0;
      var y = LX(S);
      if (AX[y])
        return;
      AX[y] = !0;
      var d = "";
      if (M && M._owner && M._owner !== o.current)
        d = " It was passed a child from " + W0(M._owner.type) + ".";
      g1(M), x0('Each child in a list should have a unique "key" prop.%s%s See https://fb.me/react-warning-keys for more information.', y, d), g1(null);
    }
    function _4(M, S) {
      if (typeof M !== "object")
        return;
      if (Array.isArray(M))
        for (var y = 0;y < M.length; y++) {
          var d = M[y];
          if (Q0(d))
            I4(d, S);
        }
      else if (Q0(M)) {
        if (M._store)
          M._store.validated = !0;
      } else if (M) {
        var K0 = c0(M);
        if (typeof K0 === "function") {
          if (K0 !== M.entries) {
            var H1 = K0.call(M), _0;
            while (!(_0 = H1.next()).done)
              if (Q0(_0.value))
                I4(_0.value, S);
          }
        }
      }
    }
    function T4(M) {
      {
        var S = M.type;
        if (S === null || S === void 0 || typeof S === "string")
          return;
        var y = W0(S), d;
        if (typeof S === "function")
          d = S.propTypes;
        else if (typeof S === "object" && (S.$$typeof === V || S.$$typeof === i))
          d = S.propTypes;
        else
          return;
        if (d)
          g1(M), J(d, M.props, "prop", y, v0.getStackAddendum), g1(null);
        else if (S.PropTypes !== void 0 && !bJ)
          bJ = !0, x0("Component %s declared `PropTypes` instead of `propTypes`. Did you misspell the property assignment?", y || "Unknown");
        if (typeof S.getDefaultProps === "function" && !S.getDefaultProps.isReactClassApproved)
          x0("getDefaultProps is only used on classic React.createClass definitions. Use a static property named `defaultProps` instead.");
      }
    }
    function uJ(M) {
      {
        g1(M);
        var S = Object.keys(M.props);
        for (var y = 0;y < S.length; y++) {
          var d = S[y];
          if (d !== "children" && d !== "key") {
            x0("Invalid prop `%s` supplied to `React.Fragment`. React.Fragment can only have `key` and `children` props.", d);
            break;
          }
        }
        if (M.ref !== null)
          x0("Invalid attribute `ref` supplied to `React.Fragment`.");
        g1(null);
      }
    }
    function g4(M, S, y) {
      var d = HQ(M);
      if (!d) {
        var K0 = "";
        if (M === void 0 || typeof M === "object" && M !== null && Object.keys(M).length === 0)
          K0 += " You likely forgot to export your component from the file it's defined in, or you might have mixed up default and named imports.";
        var H1 = K1(S);
        if (H1)
          K0 += H1;
        else
          K0 += o$();
        var _0;
        if (M === null)
          _0 = "null";
        else if (Array.isArray(M))
          _0 = "array";
        else if (M !== void 0 && M.$$typeof === K)
          _0 = "<" + (W0(M.type) || "Unknown") + " />", K0 = " Did you accidentally export a JSX literal instead of a component?";
        else
          _0 = typeof M;
        x0("React.createElement: type is invalid -- expected a string (for built-in components) or a class/function (for composite components) but got: %s.%s", _0, K0);
      }
      var d0 = p8.apply(this, arguments);
      if (d0 == null)
        return d0;
      if (d)
        for (var O6 = 2;O6 < arguments.length; O6++)
          _4(arguments[O6], M);
      if (M === N)
        uJ(d0);
      else
        T4(d0);
      return d0;
    }
    var x4 = !1;
    function cJ(M) {
      var S = g4.bind(null, M);
      S.type = M;
      {
        if (!x4)
          x4 = !0, U1("React.createFactory() is deprecated and will be removed in a future major release. Consider using JSX or use React.createElement() directly instead.");
        Object.defineProperty(S, "type", {
          enumerable: !1,
          get: function() {
            return U1("Factory.type is deprecated. Access the class directly before passing it to createFactory."), Object.defineProperty(this, "type", {
              value: M
            }), M;
          }
        });
      }
      return S;
    }
    function a$(M, S, y) {
      var d = jQ.apply(this, arguments);
      for (var K0 = 2;K0 < arguments.length; K0++)
        _4(arguments[K0], d.type);
      return T4(d), d;
    }
    try {
      var r$ = Object.freeze({}), pJ = /* @__PURE__ */ new Map([[r$, null]]), sX = /* @__PURE__ */ new Set([r$]);
      pJ.set(0, 0), sX.add(0);
    } catch (M) {}
    var CQ = g4, OX = a$, wX = cJ, v4 = {
      map: y6,
      forEach: H8,
      count: BQ,
      toArray: s8,
      only: o8
    };
    fx.Children = v4, fx.Component = x1, fx.Fragment = N, fx.Profiler = L, fx.PureComponent = C1, fx.StrictMode = F, fx.Suspense = g, fx.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED = _1, fx.cloneElement = OX, fx.createContext = KQ, fx.createElement = CQ, fx.createFactory = wX, fx.createRef = h6, fx.forwardRef = pQ, fx.isValidElement = Q0, fx.lazy = PX, fx.memo = fZ, fx.useCallback = s$, fx.useContext = V4, fx.useDebugValue = fq, fx.useEffect = xq, fx.useImperativeHandle = yq, fx.useLayoutEffect = vq, fx.useMemo = hq, fx.useReducer = nX, fx.useRef = n6, fx.useState = S4, fx.version = Y;
  })();
});

// node_modules/pdb-parser-js/dist/extension/string.js
var x6 = $6((mk) => {
  Object.defineProperty(mk, "__esModule", { value: !0 });
  mk.toFloatOrNull = mk.toIntOrNull = void 0;
  String.prototype.extract = function(Q, J) {
    try {
      let Y = this.substring(Q - 1, J).trim();
      return Y.isEmpty() ? null : Y;
    } catch (Y) {
      return console.warn(Y), null;
    }
  };
  String.prototype.isEmpty = function() {
    return !this || !this.length;
  };
  String.prototype.isBlank = function() {
    return !this || !this.trim().length;
  };
  function tf(Q) {
    if (Q) {
      let J = parseInt(Q);
      return isNaN(J) ? null : J;
    }
    return null;
  }
  mk.toIntOrNull = tf;
  function ef(Q) {
    if (Q) {
      let J = parseFloat(Q);
      return isNaN(J) ? null : J;
    }
    return null;
  }
  mk.toFloatOrNull = ef;
});

// node_modules/pdb-parser-js/dist/parser.js
var gZ = $6((pk) => {
  Object.defineProperty(pk, "__esModule", { value: !0 });
  pk.SectionParser = pk.AbstractParser = void 0;

  class uk {
    lines = [];
    collect(Q) {
      if (Array.isArray(Q)) {
        for (let J of Q)
          if (this.match(J))
            this.lines.push(J);
      } else if (this.match(Q))
        this.lines.push(Q);
    }
    parse() {
      let Q = this._parse();
      if (this.validate(Q))
        return Q;
      else
        throw Error("validate error");
    }
    validate(Q) {
      return !0;
    }
  }
  pk.AbstractParser = uk;

  class ck {
    collect(Q) {
      if (Array.isArray(Q))
        for (let J of Q)
          for (let Y of this.parsers())
            Y.collect(J);
      else
        for (let J of this.parsers())
          J.collect(Q);
    }
  }
  pk.SectionParser = ck;
});

// node_modules/pdb-parser-js/dist/section/title.js
var MF = $6((nk) => {
  Object.defineProperty(nk, "__esModule", { value: !0 });
  nk.TitleSectionParser = nk.Remark470Parser = nk.Remark465Parser = nk.Remark350Parser = nk.Remark4Parser = nk.RemarkParser = nk.SprsdeParser = nk.RevdatParser = nk.AuthorParser = nk.MdltypParser = nk.NummdlParser = nk.ExpdtaParser = nk.KeywdsParser = nk.SourceParser = nk.CompndParser = nk.CaveatParser = nk.SplitParser = nk.TitleParser = nk.ObslteParser = nk.HeaderParser = nk.Biomt = void 0;
  x6();
  var DQ = gZ(), NX = x6();

  class ZF {
    recordName;
    serial;
    Mn1;
    Mn2;
    Mn3;
    Vn;
    constructor(Q, J, Y, W, K, z) {
      this.recordName = Q, this.serial = J, this.Mn1 = Y, this.Mn2 = W, this.Mn3 = K, this.Vn = z;
    }
    toPoint4D() {
      return [this.Mn1, this.Mn2, this.Mn3, this.Vn];
    }
  }
  nk.Biomt = ZF;

  class XF extends DQ.AbstractParser {
    match(Q) {
      return Q.startsWith("HEADER");
    }
    _parse() {
      let Q = {
        classification: null,
        depDate: null,
        idCode: null
      };
      if (this.lines.length == 0)
        return Q;
      let J = this.lines[0], Y = J.extract(11, 50), W = J.extract(51, 59), K = J.extract(63, 66);
      return {
        ...Q,
        classification: Y,
        depDate: W,
        idCode: K
      };
    }
  }
  nk.HeaderParser = XF;

  class JF extends DQ.AbstractParser {
    match(Q) {
      return Q.startsWith("OBSLTE");
    }
    _parse() {
      return this.lines.map((Q) => {
        let J = Q.extract(12, 20), Y = Q.extract(22, 25), W = [
          Q.extract(32, 35),
          Q.extract(37, 40),
          Q.extract(42, 45),
          Q.extract(47, 50),
          Q.extract(52, 55),
          Q.extract(57, 60),
          Q.extract(62, 65),
          Q.extract(67, 70),
          Q.extract(72, 75)
        ];
        return {
          repDate: J,
          idCode: Y,
          rIdCodes: W.filter((K) => K)
        };
      });
    }
  }
  nk.ObslteParser = JF;

  class $F extends DQ.AbstractParser {
    match(Q) {
      return Q.startsWith("TITLE ");
    }
    _parse() {
      let Q = this.lines.map((J) => J.extract(11)).join(" ");
      if (Q.isBlank())
        return null;
      return Q;
    }
  }
  nk.TitleParser = $F;

  class YF extends DQ.AbstractParser {
    match(Q) {
      return Q.startsWith("SPLIT ");
    }
    _parse() {
      return this.lines.flatMap((Q) => {
        return [
          Q.extract(12, 15),
          Q.extract(17, 20),
          Q.extract(22, 25),
          Q.extract(27, 30),
          Q.extract(32, 35),
          Q.extract(37, 40),
          Q.extract(42, 45),
          Q.extract(47, 50),
          Q.extract(52, 55),
          Q.extract(57, 60),
          Q.extract(62, 65),
          Q.extract(67, 70),
          Q.extract(72, 75),
          Q.extract(77, 80)
        ].filter((J) => J);
      });
    }
  }
  nk.SplitParser = YF;

  class qF extends DQ.AbstractParser {
    match(Q) {
      return Q.startsWith("CAVEAT");
    }
    _parse() {
      return this.lines.flatMap((Q) => {
        let J = Q.extract(12, 15), Y = Q.extract(20, 79);
        return {
          idCode: J,
          comment: Y
        };
      });
    }
  }
  nk.CaveatParser = qF;

  class WF extends DQ.AbstractParser {
    isTokenBegin(Q) {
      let J = this.tokens();
      for (let Y of J)
        if (Q.startsWith(`${Y}:`))
          return !0;
      return !1;
    }
    _parse() {
      let Q = this.lines.map((K) => K.extract(11, 80)).filter((K) => K), J = [];
      for (let K of Q) {
        if (!K)
          continue;
        if (this.isTokenBegin(K))
          J.push(K);
        else
          J[J.length - 1] += K;
      }
      let Y = [], W = null;
      for (let K of J) {
        if (K.startsWith("MOL_ID:")) {
          if (W != null)
            Y.push(W);
          W = {};
        }
        let z = K.indexOf(":"), N = K.substring(0, z), F = K.substring(z + 1).trim();
        W[N] = F.endsWith(";") ? F.slice(0, -1) : F;
      }
      if (W != null)
        Y.push(W);
      return Y;
    }
  }

  class KF extends WF {
    tokens() {
      return [
        "MOL_ID",
        "MOLECULE",
        "CHAIN",
        "FRAGMENT",
        "SYNONYM",
        "EC",
        "ENGINEERED",
        "MUTATION",
        "OTHER_DETAILS"
      ];
    }
    match(Q) {
      return Q.startsWith("COMPND");
    }
  }
  nk.CompndParser = KF;

  class HF extends WF {
    tokens() {
      return [
        "MOL_ID",
        "SYNTHETIC",
        "FRAGMENT",
        "ORGANISM_SCIENTIFIC",
        "ORGANISM_COMMON",
        "ORGANISM_TAXID",
        "STRAIN",
        "VARIANT",
        "CELL_LINE",
        "ATCC",
        "ORGAN",
        "TISSUE",
        "CELL",
        "ORGANELLE",
        "SECRETION",
        "CELLULAR_LOCATION",
        "PLASMID",
        "GENE",
        "EXPRESSION_SYSTEM",
        "EXPRESSION_SYSTEM_COMMON",
        "EXPRESSION_SYSTEM_TAXID",
        "EXPRESSION_SYSTEM_STRAIN",
        "EXPRESSION_SYSTEM_VARIANT",
        "EXPRESSION_SYSTEM_CELL_LINE",
        "EXPRESSION_SYSTEM_ATCC_NUMBER",
        "EXPRESSION_SYSTEM_ORGAN",
        "EXPRESSION_SYSTEM_TISSUE",
        "EXPRESSION_SYSTEM_CELL",
        "EXPRESSION_SYSTEM_ORGANELLE",
        "EXPRESSION_SYSTEM_CELLULAR_LOCATION",
        "EXPRESSION_SYSTEM_VECTOR_TYPE",
        "EXPRESSION_SYSTEM_VECTOR",
        "EXPRESSION_SYSTEM_PLASMID",
        "EXPRESSION_SYSTEM_GENE",
        "OTHER_DETAILS"
      ];
    }
    match(Q) {
      return Q.startsWith("SOURCE");
    }
  }
  nk.SourceParser = HF;

  class GF extends DQ.AbstractParser {
    match(Q) {
      return Q.startsWith("KEYWDS");
    }
    _parse() {
      return this.lines.map((Q) => Q.extract(11)).filter((Q) => Q).join("").split(",").map((Q) => Q.trim()).filter((Q) => Q);
    }
  }
  nk.KeywdsParser = GF;

  class zF extends DQ.AbstractParser {
    match(Q) {
      return Q.startsWith("EXPDTA");
    }
    _parse() {
      return this.lines.map((Q) => Q.extract(11)).filter((Q) => Q);
    }
  }
  nk.ExpdtaParser = zF;

  class NF extends DQ.AbstractParser {
    match(Q) {
      return Q.startsWith("NUMMDL");
    }
    _parse() {
      if (this.lines.length == 0)
        return null;
      let J = this.lines[0].extract(11, 14);
      return NX.toIntOrNull(J);
    }
  }
  nk.NummdlParser = NF;

  class EF extends DQ.AbstractParser {
    match(Q) {
      return Q.startsWith("MDLTYP");
    }
    _parse() {
      return this.lines.map((Q) => Q.extract(11, 48)).filter((Q) => Q);
    }
  }
  nk.MdltypParser = EF;

  class FF extends DQ.AbstractParser {
    match(Q) {
      return Q.startsWith("AUTHOR");
    }
    _parse() {
      return this.lines.map((Q) => Q.extract(11)).filter((Q) => Q).join("").split(",").map((Q) => Q.trim()).filter((Q) => Q);
    }
  }
  nk.AuthorParser = FF;

  class UF extends DQ.AbstractParser {
    sortDesc;
    constructor(Q = !0) {
      super();
      this.sortDesc = Q;
    }
    match(Q) {
      return Q.startsWith("REVDAT");
    }
    _parse() {
      let Q = this.lines.map((W) => {
        let K = W.extract(8, 10), z = W.extract(14, 22), N = W.extract(24, 27), F = W.extract(32, 32), L = [
          W.extract(40, 45),
          W.extract(47, 52),
          W.extract(54, 59),
          W.extract(61, 66)
        ];
        return {
          modNum: NX.toIntOrNull(K),
          modDate: z,
          modId: N,
          modType: F,
          records: L.filter((w) => w)
        };
      }), J = [], Y = null;
      for (let W of Q) {
        if (W.modNum == Y) {
          let K = J.length - 1, { records: z, ...N } = { ...J[K] };
          J[K] = {
            ...N,
            records: [
              ...z,
              ...W.records
            ]
          };
        } else
          J.push(W);
        Y = W.modNum;
      }
      return J.sort((W) => W.modNum * (this.sortDesc ? 1 : -1));
    }
  }
  nk.RevdatParser = UF;

  class PF extends DQ.AbstractParser {
    match(Q) {
      return Q.startsWith("SPRSDE");
    }
    _parse() {
      return this.lines.map((Q) => {
        let J = Q.extract(12, 20), Y = Q.extract(22, 25), W = [
          Q.extract(32, 35),
          Q.extract(37, 40),
          Q.extract(42, 45),
          Q.extract(47, 50),
          Q.extract(52, 55),
          Q.extract(57, 60),
          Q.extract(62, 65),
          Q.extract(67, 70),
          Q.extract(72, 75)
        ];
        return {
          sprsdeDate: J,
          idCode: Y,
          sIdCodes: W.filter((K) => K)
        };
      });
    }
  }
  nk.SprsdeParser = PF;

  class Tq extends DQ.AbstractParser {
    match(Q) {
      if (Q.startsWith("REMARK")) {
        let J = NX.toIntOrNull(Q.extract(8, 10));
        if (this.remarkNum == J)
          return !0;
      }
      return !1;
    }
  }
  nk.RemarkParser = Tq;

  class AF extends Tq {
    remarkNum = 4;
    _parse() {
      let Q = {
        idCode: null,
        relDate: null,
        version: null
      }, J = 12, Y = this.lines.map((F) => F.extract(12)).filter((F) => F);
      if (Y.length == 0)
        return Q;
      let W = Y[0], K = W.extract(0, 4), z = W.extract(30, 33), N = W.extract(36, 44);
      return {
        ...Q,
        idCode: K,
        relDate: N,
        version: z
      };
    }
  }
  nk.Remark4Parser = AF;

  class LF extends Tq {
    remarkNum = 350;
    _parse() {
      let Q = [], J = null, Y = null, W = [], K = [];
      for (let z of this.lines) {
        if (z.extract(11, 23) == "BIOMOLECULE:") {
          if (J != null)
            Q.push({ biomolecule: J, biologicalUnit: Y, chains: [...W], biomts: [...K] }), Y = null, W.length = 0, K.length = 0;
          J = NX.toIntOrNull(z.extract(24));
        }
        if (z.extract(12, 45) == "AUTHOR DETERMINED BIOLOGICAL UNIT:")
          Y = z.extract(47);
        if (z.extract(12, 41) == "APPLY THE FOLLOWING TO CHAINS:" || z.extract(12, 41) == "AND CHAINS:")
          z.extract(43)?.split(",")?.forEach((N) => {
            let F = N.trim();
            if (F)
              W.push(F);
          });
        if (z.extract(14, 18) == "BIOMT") {
          let N = z.split(/\s+/);
          K.push(new ZF(N[2], NX.toIntOrNull(N[3]), NX.toFloatOrNull(N[4]), NX.toFloatOrNull(N[5]), NX.toFloatOrNull(N[6]), NX.toFloatOrNull(N[7])));
        }
      }
      return Q.push({ biomolecule: J, biologicalUnit: Y, chains: [...W], biomts: [...K] }), Q;
    }
  }
  nk.Remark350Parser = LF;

  class OF extends Tq {
    remarkNum = 465;
    _parse() {
      let Q = [], J = !1;
      for (let Y of this.lines)
        if (J) {
          let W = Y.extract(16, 19), K = Y.extract(20, 20), z = Y.extract(22, 26), N = Y.extract(27, 27);
          Q.push({
            resName: W,
            chainID: K,
            resSeq: NX.toIntOrNull(z),
            iCode: N
          });
        } else if (Y.includes("RES C SSSEQI"))
          J = !0;
      return Q;
    }
  }
  nk.Remark465Parser = OF;

  class wF extends Tq {
    remarkNum = 470;
    _parse() {
      let Q = (W, K, z, N, F) => {
        return {
          resName: W,
          chainID: K,
          resSeq: NX.toIntOrNull(z),
          iCode: N,
          atoms: F?.split(" ")?.map((L) => L.trim())?.filter((L) => L) ?? []
        };
      }, J = [], Y = null;
      for (let W of this.lines)
        switch (Y) {
          case "NonNMR": {
            let K = W.extract(16, 19), z = W.extract(21, 21), N = W.extract(22, 25), F = W.extract(26, 26), L = W.extract(29);
            J.push(Q(K, z, N, F, L));
            break;
          }
          case "NMR": {
            let K = W.extract(16, 19), z = W.extract(20, 20), N = W.extract(21, 24), F = W.extract(25, 25), L = W.extract(28);
            J.push(Q(K, z, N, F, L));
            break;
          }
          default:
            if (W.includes("RES  CSSEQI  ATOMS"))
              Y = "NonNMR";
            else if (W.includes("RES CSSEQI  ATOMS"))
              Y = "NMR";
            break;
        }
      return J;
    }
  }
  nk.Remark470Parser = wF;

  class lk extends DQ.SectionParser {
    headerParser = new XF;
    obslteParser = new JF;
    titleParser = new $F;
    splitParser = new YF;
    caveatParser = new qF;
    compndParser = new KF;
    sourceParser = new HF;
    keywdsParser = new GF;
    expdtaParser = new zF;
    nummdlParser = new NF;
    mdltypParser = new EF;
    authorParser = new FF;
    revdatParser = new UF;
    sprsdeParser = new PF;
    remark4Parser = new AF;
    remark350Parser = new LF;
    remark465Parser = new OF;
    remark470Parser = new wF;
    parsers() {
      return [
        this.headerParser,
        this.obslteParser,
        this.titleParser,
        this.splitParser,
        this.caveatParser,
        this.compndParser,
        this.sourceParser,
        this.keywdsParser,
        this.expdtaParser,
        this.nummdlParser,
        this.mdltypParser,
        this.authorParser,
        this.revdatParser,
        this.sprsdeParser,
        this.remark4Parser,
        this.remark350Parser,
        this.remark465Parser,
        this.remark470Parser
      ];
    }
    parse() {
      return {
        header: this.headerParser.parse(),
        obsltes: this.obslteParser.parse(),
        title: this.titleParser.parse(),
        splits: this.splitParser.parse(),
        caveats: this.caveatParser.parse(),
        compnds: this.compndParser.parse(),
        sources: this.sourceParser.parse(),
        keywds: this.keywdsParser.parse(),
        expdtas: this.expdtaParser.parse(),
        nummdl: this.nummdlParser.parse(),
        mdltyps: this.mdltypParser.parse(),
        authors: this.authorParser.parse(),
        revdats: this.revdatParser.parse(),
        sprsdes: this.sprsdeParser.parse(),
        remark4: this.remark4Parser.parse(),
        remark350: this.remark350Parser.parse(),
        missingResidues: this.remark465Parser.parse(),
        missingAtoms: this.remark470Parser.parse()
      };
    }
  }
  nk.TitleSectionParser = lk;
});

// node_modules/pdb-parser-js/dist/section/primaryStructure.js
var VF = $6((rk) => {
  Object.defineProperty(rk, "__esModule", { value: !0 });
  rk.PrimaryStructureSectionParser = rk.SeqresParser = rk.Dbref2Parser = rk.Dbref1Parser = rk.ModresParser = rk.SeqadvParser = rk.DbrefParser = void 0;
  x6();
  var l$ = gZ(), HZ = x6();

  class ok {
    idCode;
    resName;
    chainID;
    resSeq;
    iCode;
    database;
    dbAccession;
    dbRes;
    dbSeq;
    conflict;
    constructor(Q, J, Y, W, K, z, N, F, L, w) {
      this.idCode = Q, this.resName = J, this.chainID = Y, this.resSeq = W, this.iCode = K, this.database = z, this.dbAccession = N, this.dbRes = F, this.dbSeq = L, this.conflict = w;
    }
    isMutation() {
      return this.conflict == "ENGINEERED MUTATION";
    }
  }

  class DF extends l$.AbstractParser {
    match(Q) {
      return Q.startsWith("DBREF ");
    }
    _parse() {
      return this.lines.map((Q) => {
        let J = Q.extract(8, 11), Y = Q.extract(13, 13), W = Q.extract(15, 18), K = Q.extract(19, 19), z = Q.extract(21, 24), N = Q.extract(25, 25), F = Q.extract(27, 32), L = Q.extract(34, 41), w = Q.extract(43, 54), D = Q.extract(56, 60), R = Q.extract(61, 61), V = Q.extract(63, 67), g = Q.extract(68, 68);
        return {
          idCode: J,
          chainID: Y,
          seqBegin: HZ.toIntOrNull(W),
          insertBegin: K,
          seqEnd: HZ.toIntOrNull(z),
          insertEnd: N,
          database: F,
          dbAccession: L,
          dbIdCode: w,
          dbseqBegin: HZ.toIntOrNull(D),
          idbnsBeg: R,
          dbseqEnd: HZ.toIntOrNull(V),
          dbinsEnd: g
        };
      });
    }
  }
  rk.DbrefParser = DF;

  class kF extends l$.AbstractParser {
    match(Q) {
      return Q.startsWith("SEQADV");
    }
    _parse() {
      return this.lines.map((Q) => {
        let J = Q.extract(8, 11), Y = Q.extract(13, 15), W = Q.extract(17, 17), K = Q.extract(19, 22), z = Q.extract(23, 23), N = Q.extract(25, 28), F = Q.extract(30, 38), L = Q.extract(40, 42), w = Q.extract(44, 48), D = Q.extract(50, 70);
        return new ok(J, Y, W, HZ.toIntOrNull(K), z, N, F, L, HZ.toIntOrNull(w), D);
      });
    }
  }
  rk.SeqadvParser = kF;

  class RF extends l$.AbstractParser {
    match(Q) {
      return Q.startsWith("MODRES");
    }
    _parse() {
      return this.lines.map((Q) => {
        let J = Q.extract(8, 11), Y = Q.extract(13, 15), W = Q.extract(17, 17), K = Q.extract(19, 22), z = Q.extract(23, 23), N = Q.extract(25, 27), F = Q.extract(30, 70);
        return {
          idCode: J,
          resName: Y,
          chainID: W,
          resSeq: HZ.toIntOrNull(K),
          iCode: z,
          stdRes: N,
          comment: F
        };
      });
    }
  }
  rk.ModresParser = RF;

  class jF extends l$.AbstractParser {
    match(Q) {
      return Q.startsWith("DBREF1");
    }
    _parse() {
      return this.lines.map((Q) => {
        let J = Q.extract(8, 11), Y = Q.extract(13, 13), W = Q.extract(15, 18), K = Q.extract(19, 19), z = Q.extract(21, 24), N = Q.extract(25, 25), F = Q.extract(27, 32), L = Q.extract(48, 67);
        return {
          idCode: J,
          chainID: Y,
          seqBegin: HZ.toIntOrNull(W),
          insertBegin: K,
          seqEnd: HZ.toIntOrNull(z),
          insertEnd: N,
          database: F,
          dbIdCode: L
        };
      });
    }
  }
  rk.Dbref1Parser = jF;

  class BF extends l$.AbstractParser {
    match(Q) {
      return Q.startsWith("DBREF2");
    }
    _parse() {
      return this.lines.map((Q) => {
        let J = Q.extract(8, 11), Y = Q.extract(13, 13), W = Q.extract(19, 40), K = Q.extract(46, 55), z = Q.extract(58, 67);
        return {
          idCode: J,
          chainID: Y,
          dbAccession: W,
          seqBegin: HZ.toIntOrNull(K),
          seqEnd: HZ.toIntOrNull(z)
        };
      });
    }
  }
  rk.Dbref2Parser = BF;

  class CF extends l$.AbstractParser {
    match(Q) {
      return Q.startsWith("SEQRES");
    }
    _parse() {
      return this.lines.map((Q) => {
        let J = Q.extract(8, 10), Y = Q.extract(12, 12), W = Q.extract(14, 17), K = [
          Q.extract(20, 22),
          Q.extract(24, 26),
          Q.extract(28, 30),
          Q.extract(32, 34),
          Q.extract(36, 38),
          Q.extract(40, 42),
          Q.extract(44, 46),
          Q.extract(48, 50),
          Q.extract(52, 54),
          Q.extract(56, 58),
          Q.extract(60, 62),
          Q.extract(64, 66),
          Q.extract(68, 70)
        ];
        return {
          serNum: HZ.toIntOrNull(J),
          chainID: Y,
          numRes: HZ.toIntOrNull(W),
          resNames: K.filter((z) => z)
        };
      });
    }
  }
  rk.SeqresParser = CF;

  class ak extends l$.SectionParser {
    dbrefParser = new DF;
    seqadvParser = new kF;
    modresParser = new RF;
    dbref1Parser = new jF;
    dbref2Parser = new BF;
    seqresParser = new CF;
    parsers() {
      return [
        this.dbrefParser,
        this.seqadvParser,
        this.modresParser,
        this.dbref1Parser,
        this.dbref2Parser,
        this.seqresParser
      ];
    }
    parse() {
      return {
        dbrefs: this.dbrefParser.parse(),
        seqadvs: this.seqadvParser.parse(),
        modress: this.modresParser.parse(),
        dbref1s: this.dbref1Parser.parse(),
        dbref2s: this.dbref2Parser.parse(),
        seqress: this.seqresParser.parse()
      };
    }
  }
  rk.PrimaryStructureSectionParser = ak;
});

// node_modules/pdb-parser-js/dist/section/heterogen.js
var gF = $6((ek) => {
  Object.defineProperty(ek, "__esModule", { value: !0 });
  ek.HeterogenSectionParser = ek.FormulParser = ek.HetsynParser = ek.HetnamParser = ek.HetParser = void 0;
  x6();
  var HK = gZ(), X7 = x6();

  class SF extends HK.AbstractParser {
    match(Q) {
      return Q.startsWith("HET   ");
    }
    _parse() {
      return this.lines.map((Q) => {
        let J = Q.extract(8, 10), Y = Q.extract(13, 13), W = Q.extract(14, 17), K = Q.extract(18, 18), z = Q.extract(21, 25), N = Q.extract(31, 70);
        return {
          hetID: J,
          chainID: Y,
          seqNum: X7.toIntOrNull(W),
          iCode: K,
          numHetAtoms: X7.toIntOrNull(z),
          text: N
        };
      });
    }
  }
  ek.HetParser = SF;

  class IF extends HK.AbstractParser {
    match(Q) {
      return Q.startsWith("HETNAM");
    }
    _parse() {
      let Q = this.lines.map((Y) => {
        let W = Y.extract(12, 14), K = Y.extract(16, 70);
        return [
          W,
          K
        ];
      }).reduce((Y, [W, K]) => {
        return Y[W] = Y[W] ?? [], Y[W].push(K), Y;
      }, {}), J = [];
      for (let Y in Q) {
        let W = Q[Y].join(" ");
        J.push({
          hetID: Y,
          text: !W.isBlank() ? W : null
        });
      }
      return J;
    }
  }
  ek.HetnamParser = IF;

  class _F extends HK.AbstractParser {
    match(Q) {
      return Q.startsWith("HETSYN");
    }
    _parse() {
      let Q = this.lines.map((Y) => {
        let W = Y.extract(12, 14), K = Y.extract(16, 70);
        return [
          W,
          K
        ];
      }).reduce((Y, [W, K]) => {
        return Y[W] = Y[W] ?? [], Y[W].push(K), Y;
      }, {}), J = [];
      for (let Y in Q) {
        let W = Q[Y].join(" ");
        J.push({
          hetID: Y,
          hetSynonyms: !W.isBlank() ? W : null
        });
      }
      return J;
    }
  }
  ek.HetsynParser = _F;

  class TF extends HK.AbstractParser {
    match(Q) {
      return Q.startsWith("FORMUL");
    }
    _parse() {
      return this.lines.map((Q) => {
        let J = Q.extract(9, 10), Y = Q.extract(13, 15), W = Q.extract(17, 18), K = Q.extract(19, 19), z = Q.extract(20, 70);
        return {
          compNum: X7.toIntOrNull(J),
          hetID: Y,
          continuation: X7.toIntOrNull(W),
          asterisk: K,
          text: z
        };
      });
    }
  }
  ek.FormulParser = TF;

  class tk extends HK.SectionParser {
    hetParser = new SF;
    hetnamParser = new IF;
    hetsynParser = new _F;
    formulParser = new TF;
    parsers() {
      return [this.hetParser, this.hetnamParser, this.hetsynParser, this.formulParser];
    }
    parse() {
      return {
        hets: this.hetParser.parse(),
        hetnams: this.hetnamParser.parse(),
        hetsyns: this.hetsynParser.parse(),
        formuls: this.formulParser.parse()
      };
    }
  }
  ek.HeterogenSectionParser = tk;
});

// node_modules/pdb-parser-js/dist/section/secondaryStructure.js
var yF = $6((XR) => {
  Object.defineProperty(XR, "__esModule", { value: !0 });
  XR.SecondaryStructureSectionParser = XR.SheetParser = XR.HelixParser = void 0;
  x6();
  var xF = gZ(), xZ = x6();

  class vF extends xF.AbstractParser {
    match(Q) {
      return Q.startsWith("HELIX ");
    }
    _parse() {
      return this.lines.map((Q) => {
        let J = Q.extract(8, 10), Y = Q.extract(12, 14), W = Q.extract(16, 18), K = Q.extract(20, 20), z = Q.extract(22, 25), N = Q.extract(26, 26), F = Q.extract(28, 30), L = Q.extract(32, 32), w = Q.extract(34, 37), D = Q.extract(38, 38), R = Q.extract(39, 40), V = Q.extract(41, 70), g = Q.extract(72, 76);
        return {
          serNum: xZ.toIntOrNull(J),
          helixID: Y,
          initResidue: {
            resName: W,
            chainID: K,
            resSeq: xZ.toIntOrNull(z),
            iCode: N
          },
          endResidue: {
            resName: F,
            chainID: L,
            resSeq: xZ.toIntOrNull(w),
            iCode: D
          },
          helixClass: xZ.toIntOrNull(R),
          comment: V,
          length: xZ.toIntOrNull(g)
        };
      });
    }
  }
  XR.HelixParser = vF;

  class hF extends xF.AbstractParser {
    match(Q) {
      return Q.startsWith("SHEET ");
    }
    _parse() {
      return this.lines.map((Q) => {
        let J = Q.extract(8, 10), Y = Q.extract(12, 14), W = Q.extract(15, 16), K = Q.extract(18, 20), z = Q.extract(22, 22), N = Q.extract(23, 26), F = Q.extract(27, 27), L = Q.extract(29, 31), w = Q.extract(33, 33), D = Q.extract(34, 37), R = Q.extract(38, 38), V = Q.extract(39, 40), g = Q.extract(42, 45), s = Q.extract(46, 48), i = Q.extract(50, 50), F0 = Q.extract(51, 54), r = Q.extract(55, 55), J0 = Q.extract(57, 60), l = Q.extract(61, 63), t = Q.extract(65, 65), $0 = Q.extract(66, 69), M0 = Q.extract(70, 70);
        return {
          strand: xZ.toIntOrNull(J),
          sheetID: Y,
          numStrands: xZ.toIntOrNull(W),
          initResidue: {
            resName: K,
            chainID: z,
            resSeq: xZ.toIntOrNull(N),
            iCode: F
          },
          endResidue: {
            resName: L,
            chainID: w,
            resSeq: xZ.toIntOrNull(D),
            iCode: R
          },
          sense: xZ.toIntOrNull(V),
          curResidue: {
            atom: g,
            resName: s,
            chainID: i,
            resSeq: xZ.toIntOrNull(F0),
            iCode: r
          },
          prevResidue: {
            atom: J0,
            resName: l,
            chainID: t,
            resSeq: xZ.toIntOrNull($0),
            iCode: M0
          }
        };
      });
    }
  }
  XR.SheetParser = hF;

  class ZR extends xF.SectionParser {
    helixParser = new vF;
    sheetParser = new hF;
    parsers() {
      return [
        this.helixParser,
        this.sheetParser
      ];
    }
    parse() {
      return {
        helixs: this.helixParser.parse(),
        sheets: this.sheetParser.parse()
      };
    }
  }
  XR.SecondaryStructureSectionParser = ZR;
});

// node_modules/pdb-parser-js/dist/section/connectivityAnnotation.js
var uF = $6((YR) => {
  Object.defineProperty(YR, "__esModule", { value: !0 });
  YR.ConnectivityAnnotationSectionParser = YR.CispepParser = YR.LinkParser = YR.SsbondParser = void 0;
  x6();
  var J7 = gZ(), vZ = x6();

  class fF extends J7.AbstractParser {
    match(Q) {
      return Q.startsWith("SSBOND");
    }
    _parse() {
      return this.lines.map((Q) => {
        let J = Q.extract(8, 10), Y = Q.extract(12, 14), W = Q.extract(16, 16), K = Q.extract(18, 21), z = Q.extract(22, 22), N = Q.extract(26, 28), F = Q.extract(30, 30), L = Q.extract(32, 35), w = Q.extract(36, 36), D = Q.extract(60, 65), R = Q.extract(67, 72), V = Q.extract(74, 78);
        return {
          serNum: vZ.toIntOrNull(J),
          residue1: {
            resName: Y ?? "CYS",
            chainID: W,
            resSeq: vZ.toIntOrNull(K),
            iCode: z
          },
          residue2: {
            resName: N ?? "CYS",
            chainID: F,
            resSeq: vZ.toIntOrNull(L),
            iCode: w
          },
          sym1: D,
          sym2: R,
          Length: vZ.toFloatOrNull(V)
        };
      });
    }
  }
  YR.SsbondParser = fF;

  class mF extends J7.AbstractParser {
    match(Q) {
      return Q.startsWith("LINK  ");
    }
    _parse() {
      return this.lines.map((Q) => {
        let J = Q.extract(13, 16), Y = Q.extract(17, 17), W = Q.extract(18, 20), K = Q.extract(22, 22), z = Q.extract(23, 26), N = Q.extract(27, 27), F = Q.extract(43, 46), L = Q.extract(47, 47), w = Q.extract(48, 50), D = Q.extract(52, 52), R = Q.extract(53, 56), V = Q.extract(57, 57), g = Q.extract(60, 65), s = Q.extract(67, 72), i = Q.extract(74, 78);
        return {
          residue1: {
            atom: J,
            altLoc: Y,
            resName: W,
            chainID: K,
            resSeq: vZ.toIntOrNull(z),
            iCode: N
          },
          residue2: {
            atom: F,
            altLoc: L,
            resName: w,
            chainID: D,
            resSeq: vZ.toIntOrNull(R),
            iCode: V
          },
          sym1: g,
          sym2: s,
          Length: vZ.toFloatOrNull(i)
        };
      });
    }
  }
  YR.LinkParser = mF;

  class bF extends J7.AbstractParser {
    match(Q) {
      return Q.startsWith("CISPEP");
    }
    _parse() {
      return this.lines.map((Q) => {
        let J = Q.extract(8, 10), Y = Q.extract(12, 14), W = Q.extract(16, 16), K = Q.extract(18, 21), z = Q.extract(22, 22), N = Q.extract(26, 28), F = Q.extract(30, 30), L = Q.extract(32, 35), w = Q.extract(36, 36), D = Q.extract(44, 46), R = Q.extract(54, 59);
        return {
          serNum: vZ.toIntOrNull(J),
          residue1: {
            resName: Y,
            chainID: W,
            resSeq: vZ.toIntOrNull(K),
            iCode: z
          },
          residue2: {
            resName: N,
            chainID: F,
            resSeq: vZ.toIntOrNull(L),
            iCode: w
          },
          modNum: vZ.toIntOrNull(D),
          measure: vZ.toFloatOrNull(R)
        };
      });
    }
  }
  YR.CispepParser = bF;

  class $R extends J7.SectionParser {
    ssbondParser = new fF;
    linkParser = new mF;
    cispepParser = new bF;
    parsers() {
      return [this.ssbondParser, this.linkParser, this.cispepParser];
    }
    parse() {
      return {
        ssbonds: this.ssbondParser.parse(),
        links: this.linkParser.parse(),
        cispeps: this.cispepParser.parse()
      };
    }
  }
  YR.ConnectivityAnnotationSectionParser = $R;
});

// node_modules/pdb-parser-js/dist/section/miscellaneousFeatures.js
var dF = $6((HR) => {
  Object.defineProperty(HR, "__esModule", { value: !0 });
  HR.MiscellaneousFeaturesSectionParser = HR.SiteParser = void 0;
  x6();
  var WR = gZ(), cF = x6();

  class pF extends WR.AbstractParser {
    match(Q) {
      return Q.startsWith("SITE  ");
    }
    _parse() {
      let Q = (J, Y, W, K) => {
        if (J == null || Y == null || W == null)
          return null;
        return {
          resName: J,
          chainID: Y,
          resSeq: cF.toIntOrNull(W),
          iCode: K
        };
      };
      return this.lines.map((J) => {
        let Y = J.extract(8, 10), W = J.extract(12, 14), K = J.extract(16, 17), z = J.extract(19, 21), N = J.extract(23, 23), F = J.extract(24, 27), L = J.extract(28, 28), w = J.extract(30, 32), D = J.extract(34, 34), R = J.extract(35, 38), V = J.extract(39, 39), g = J.extract(41, 43), s = J.extract(45, 45), i = J.extract(46, 49), F0 = J.extract(50, 50), r = J.extract(52, 54), J0 = J.extract(56, 56), l = J.extract(57, 60), t = J.extract(61, 61);
        return {
          seqNum: cF.toIntOrNull(Y),
          siteID: W,
          numRes: cF.toIntOrNull(K),
          residues: [
            Q(z, N, F, L),
            Q(w, D, R, V),
            Q(g, s, i, F0),
            Q(r, J0, l, t)
          ].filter(($0) => $0)
        };
      });
    }
    validate(Q) {
      let J = Q.reduce((Y, W) => {
        let K = W.siteID + "\t" + W.numRes;
        return Y[K] = Y[K] ?? [], Y[K].push(...W.residues), Y;
      }, {});
      for (let Y in J) {
        let [W, K] = Y.split("\t"), z = J[Y].length;
        if (parseInt(K) != z)
          return console.error(`"${W}" length error. expected : ${K}, actual : ${z}`), !1;
      }
      return !0;
    }
  }
  HR.SiteParser = pF;

  class KR extends WR.SectionParser {
    siteParser = new pF;
    parsers() {
      return [this.siteParser];
    }
    parse() {
      return {
        sites: this.siteParser.parse()
      };
    }
  }
  HR.MiscellaneousFeaturesSectionParser = KR;
});

// node_modules/pdb-parser-js/dist/section/crystallographicAndCoordinateTransformation.js
var tF = $6((NR) => {
  Object.defineProperty(NR, "__esModule", { value: !0 });
  NR.CrystallographicAndCoordinateTransformationSectionParser = NR.MtrixParser = NR.ScaleParser = NR.OrigxParser = NR.Cryst1Parser = NR.Mtrix = NR.Scale = NR.Origx = void 0;
  x6();
  var GK = gZ(), v6 = x6();

  class lF {
    recordName;
    On1;
    On2;
    On3;
    Tn;
    constructor(Q, J, Y, W, K) {
      this.recordName = Q, this.On1 = J, this.On2 = Y, this.On3 = W, this.Tn = K;
    }
    toPoint4D() {
      return [this.On1, this.On2, this.On3, this.Tn];
    }
  }
  NR.Origx = lF;

  class nF {
    recordName;
    Sn1;
    Sn2;
    Sn3;
    Un;
    constructor(Q, J, Y, W, K) {
      this.recordName = Q, this.Sn1 = J, this.Sn2 = Y, this.Sn3 = W, this.Un = K;
    }
    toPoint4D() {
      return [this.Sn1, this.Sn2, this.Sn3, this.Un];
    }
  }
  NR.Scale = nF;

  class sF {
    recordName;
    serial;
    Mn1;
    Mn2;
    Mn3;
    Vn;
    iGiven;
    constructor(Q, J, Y, W, K, z, N) {
      this.recordName = Q, this.serial = J, this.Mn1 = Y, this.Mn2 = W, this.Mn3 = K, this.Vn = z, this.iGiven = N;
    }
    toPoint4D() {
      return [this.Mn1, this.Mn2, this.Mn3, this.Vn];
    }
  }
  NR.Mtrix = sF;

  class oF extends GK.AbstractParser {
    match(Q) {
      return Q.startsWith("CRYST1");
    }
    _parse() {
      if (this.lines.length == 0)
        return null;
      let Q = this.lines[0], J = Q.extract(7, 15), Y = Q.extract(16, 24), W = Q.extract(25, 33), K = Q.extract(34, 40), z = Q.extract(41, 47), N = Q.extract(48, 54), F = Q.extract(56, 66), L = Q.extract(67, 70);
      return {
        a: v6.toFloatOrNull(J),
        b: v6.toFloatOrNull(Y),
        c: v6.toFloatOrNull(W),
        alpha: v6.toFloatOrNull(K),
        beta: v6.toFloatOrNull(z),
        gamma: v6.toFloatOrNull(N),
        sGroup: F,
        z: v6.toIntOrNull(L)
      };
    }
  }
  NR.Cryst1Parser = oF;

  class aF extends GK.AbstractParser {
    match(Q) {
      return Q.startsWith("ORIGX1") || Q.startsWith("ORIGX2") || Q.startsWith("ORIGX3");
    }
    _parse() {
      return this.lines.map((Q) => {
        let J = Q.extract(1, 6), Y = Q.extract(11, 20), W = Q.extract(21, 30), K = Q.extract(31, 40), z = Q.extract(46, 55);
        return new lF(J, v6.toFloatOrNull(Y), v6.toFloatOrNull(W), v6.toFloatOrNull(K), v6.toFloatOrNull(z));
      });
    }
  }
  NR.OrigxParser = aF;

  class rF extends GK.AbstractParser {
    match(Q) {
      return Q.startsWith("SCALE1") || Q.startsWith("SCALE2") || Q.startsWith("SCALE3");
    }
    _parse() {
      return this.lines.map((Q) => {
        let J = Q.extract(1, 6), Y = Q.extract(11, 20), W = Q.extract(21, 30), K = Q.extract(31, 40), z = Q.extract(46, 55);
        return new nF(J, v6.toFloatOrNull(Y), v6.toFloatOrNull(W), v6.toFloatOrNull(K), v6.toFloatOrNull(z));
      });
    }
  }
  NR.ScaleParser = rF;

  class iF extends GK.AbstractParser {
    match(Q) {
      return Q.startsWith("MTRIX1") || Q.startsWith("MTRIX2") || Q.startsWith("MTRIX3");
    }
    _parse() {
      return this.lines.map((Q) => {
        let J = Q.extract(1, 6), Y = Q.extract(8, 11), W = Q.extract(11, 20), K = Q.extract(21, 30), z = Q.extract(31, 40), N = Q.extract(46, 55), F = Q.extract(60, 60);
        return new sF(J, v6.toIntOrNull(Y), v6.toFloatOrNull(W), v6.toFloatOrNull(K), v6.toFloatOrNull(z), v6.toFloatOrNull(N), v6.toIntOrNull(F));
      });
    }
  }
  NR.MtrixParser = iF;

  class zR extends GK.SectionParser {
    cryst1Parser = new oF;
    origxParser = new aF;
    scaleParser = new rF;
    mtrixParser = new iF;
    parsers() {
      return [
        this.cryst1Parser,
        this.origxParser,
        this.scaleParser,
        this.mtrixParser
      ];
    }
    parse() {
      return {
        cryst1: this.cryst1Parser.parse(),
        origxs: this.origxParser.parse(),
        scales: this.scaleParser.parse(),
        mtrixs: this.mtrixParser.parse()
      };
    }
  }
  NR.CrystallographicAndCoordinateTransformationSectionParser = zR;
});

// node_modules/pdb-parser-js/dist/section/coordinate.js
var $U = $6((UR) => {
  Object.defineProperty(UR, "__esModule", { value: !0 });
  UR.CoordinateSectionParser = UR.HetatmParser = UR.AnisouParser = UR.AtomParser = UR.Atom = UR.Hetatm = void 0;
  x6();
  var $7 = gZ(), kQ = x6();

  class zK {
    data;
    constructor(Q) {
      this.data = Q;
    }
    toResidue() {
      return {
        resName: this.data.resName,
        chainID: this.data.chainID,
        resSeq: this.data.resSeq,
        iCode: this.data.iCode
      };
    }
    static lineToCoordinate(Q) {
      let J = Q.extract(7, 11), Y = Q.extract(13, 16), W = Q.extract(17, 17), K = Q.extract(18, 20), z = Q.extract(22, 22), N = Q.extract(23, 26), F = Q.extract(27, 27), L = Q.extract(31, 38), w = Q.extract(39, 46), D = Q.extract(47, 54), R = Q.extract(55, 60), V = Q.extract(61, 66), g = Q.extract(77, 78), s = Q.extract(79, 80);
      return {
        serial: kQ.toIntOrNull(J),
        atom: Y,
        altLoc: W,
        resName: K,
        chainID: z,
        resSeq: kQ.toIntOrNull(N),
        iCode: F,
        x: kQ.toFloatOrNull(L),
        y: kQ.toFloatOrNull(w),
        z: kQ.toFloatOrNull(D),
        occupancy: kQ.toFloatOrNull(R),
        tempFactor: kQ.toFloatOrNull(V),
        element: g,
        charge: s
      };
    }
  }

  class eF extends zK {
    isCrystalWater() {
      return this.data.resName == "HOH";
    }
    isDummy() {
      return this.data.resName == "DUM";
    }
  }
  UR.Hetatm = eF;

  class QU extends zK {
  }
  UR.Atom = QU;

  class ZU extends $7.AbstractParser {
    filter;
    constructor(Q = null) {
      super();
      this.filter = Q;
    }
    match(Q) {
      return Q.startsWith("ATOM  ");
    }
    _parse() {
      let Q = [];
      for (let J of this.lines) {
        let Y = new QU(zK.lineToCoordinate(J));
        if (this.filter != null) {
          if (this.filter(Y))
            Q.push(Y);
        } else
          Q.push(Y);
      }
      return Q;
    }
  }
  UR.AtomParser = ZU;

  class XU extends $7.AbstractParser {
    match(Q) {
      return Q.startsWith("ANISOU");
    }
    _parse() {
      return this.lines.map((Q) => {
        let J = Q.extract(7, 11), Y = Q.extract(13, 16), W = Q.extract(17, 17), K = Q.extract(18, 20), z = Q.extract(22, 22), N = Q.extract(23, 26), F = Q.extract(27, 27), L = Q.extract(29, 35), w = Q.extract(36, 42), D = Q.extract(43, 49), R = Q.extract(50, 56), V = Q.extract(57, 63), g = Q.extract(64, 70), s = Q.extract(77, 78), i = Q.extract(79, 80);
        return {
          serial: kQ.toIntOrNull(J),
          atom: Y,
          altLoc: W,
          resName: K,
          chainID: z,
          resSeq: kQ.toIntOrNull(N),
          iCode: F,
          u00: kQ.toIntOrNull(L),
          u11: kQ.toIntOrNull(w),
          u22: kQ.toIntOrNull(D),
          u01: kQ.toIntOrNull(R),
          u02: kQ.toIntOrNull(V),
          u12: kQ.toIntOrNull(g),
          element: s,
          charge: i
        };
      });
    }
  }
  UR.AnisouParser = XU;

  class JU extends $7.AbstractParser {
    excludeDummy;
    filter;
    constructor(Q = !0, J = null) {
      super();
      this.excludeDummy = Q, this.filter = J;
    }
    match(Q) {
      if (this.excludeDummy) {
        if (Q.extract(18, 20) == "DUM")
          return !1;
      }
      return Q.startsWith("HETATM");
    }
    _parse() {
      let Q = [];
      for (let J of this.lines) {
        let Y = new eF(zK.lineToCoordinate(J));
        if (this.filter != null) {
          if (this.filter(Y))
            Q.push(Y);
        } else
          Q.push(Y);
      }
      return Q;
    }
  }
  UR.HetatmParser = JU;

  class FR extends $7.SectionParser {
    atomParer;
    anisouParser;
    hetatmParser;
    constructor(Q = !0, J = !0, Y = null, W = null) {
      super();
      this.atomParer = new ZU(Y), this.hetatmParser = new JU(Q, W), this.anisouParser = J ? null : new XU;
    }
    parsers() {
      return [this.atomParer, this.anisouParser, this.hetatmParser].filter((Q) => Q);
    }
    parse() {
      return {
        atoms: this.atomParer.parse(),
        anisous: this.anisouParser?.parse() ?? [],
        hetatms: this.hetatmParser.parse()
      };
    }
  }
  UR.CoordinateSectionParser = FR;
});

// node_modules/pdb-parser-js/dist/section/connectivity.js
var qU = $6((wR) => {
  Object.defineProperty(wR, "__esModule", { value: !0 });
  wR.ConnectivitySectionParser = wR.ConectParser = void 0;
  x6();
  var LR = gZ(), AR = x6();

  class YU extends LR.AbstractParser {
    match(Q) {
      return Q.startsWith("CONECT");
    }
    _parse() {
      return this.lines.map((Q) => {
        let J = Q.extract(7, 11), Y = [
          Q.extract(12, 16),
          Q.extract(17, 21),
          Q.extract(22, 26),
          Q.extract(27, 31)
        ];
        return {
          atomSeqNum: AR.toIntOrNull(J),
          bondedAtomSeqNums: Y.filter((W) => W).map((W) => AR.toIntOrNull(W))
        };
      });
    }
  }
  wR.ConectParser = YU;

  class OR extends LR.SectionParser {
    conectParser = new YU;
    parsers() {
      return [this.conectParser];
    }
    parse() {
      return {
        conects: this.conectParser.parse()
      };
    }
  }
  wR.ConnectivitySectionParser = OR;
});

// node_modules/pdb-parser-js/dist/section/bookkeeping.js
var KU = $6((RR) => {
  Object.defineProperty(RR, "__esModule", { value: !0 });
  RR.BookkeepingSectionParser = RR.MasterParser = void 0;
  x6();
  var DR = gZ(), EX = x6();

  class WU extends DR.AbstractParser {
    match(Q) {
      return Q.startsWith("MASTER");
    }
    _parse() {
      if (this.lines.length == 0)
        return null;
      let Q = this.lines[0], J = Q.extract(11, 15), Y = Q.extract(21, 25), W = Q.extract(26, 30), K = Q.extract(31, 35), z = Q.extract(36, 40), N = Q.extract(41, 45), F = Q.extract(46, 50), L = Q.extract(51, 55), w = Q.extract(56, 60), D = Q.extract(61, 65), R = Q.extract(66, 70);
      return {
        numRemark: EX.toIntOrNull(J),
        numHet: EX.toIntOrNull(Y),
        numHelix: EX.toIntOrNull(W),
        numSheet: EX.toIntOrNull(K),
        numTurn: EX.toIntOrNull(z),
        numSite: EX.toIntOrNull(N),
        numXform: EX.toIntOrNull(F),
        numCoord: EX.toIntOrNull(L),
        numTer: EX.toIntOrNull(w),
        numConect: EX.toIntOrNull(D),
        numSeq: EX.toIntOrNull(R)
      };
    }
  }
  RR.MasterParser = WU;

  class kR extends DR.SectionParser {
    masterParser = new WU;
    parsers() {
      return [this.masterParser];
    }
    parse() {
      return {
        master: this.masterParser.parse()
      };
    }
  }
  RR.BookkeepingSectionParser = kR;
});

// node_modules/pdb-parser-js/dist/pdb.js
var SR = $6((CR) => {
  Object.defineProperty(CR, "__esModule", { value: !0 });
  CR.PdbParser = CR.Pdb = void 0;
  var tm = MF(), em = VF(), Qb = gF(), Zb = yF(), Xb = uF(), Jb = dF(), $b = tF(), Yb = $U(), qb = qU(), Wb = KU(), Kb = gZ();

  class HU {
    title;
    primaryStructure;
    heterogen;
    secondaryStructure;
    connectivityAnnotation;
    miscellaneousFeatures;
    crystallographicAndCoordinateTransformation;
    coordinate;
    connectivity;
    bookkeeping;
    constructor(Q, J, Y, W, K, z, N, F, L, w) {
      this.title = Q, this.primaryStructure = J, this.heterogen = Y, this.secondaryStructure = W, this.connectivityAnnotation = K, this.miscellaneousFeatures = z, this.crystallographicAndCoordinateTransformation = N, this.coordinate = F, this.connectivity = L, this.bookkeeping = w;
    }
  }
  CR.Pdb = HU;

  class BR extends Kb.SectionParser {
    titleSectionParser = new tm.TitleSectionParser;
    primaryStructureSectionParser = new em.PrimaryStructureSectionParser;
    heterogenSectionParser = new Qb.HeterogenSectionParser;
    secondaryStructureSectionParser = new Zb.SecondaryStructureSectionParser;
    connectivityAnnotationSectionParser = new Xb.ConnectivityAnnotationSectionParser;
    miscellaneousFeaturesSectionParser = new Jb.MiscellaneousFeaturesSectionParser;
    crystallographicAndCoordinateTransformationSectionParser = new $b.CrystallographicAndCoordinateTransformationSectionParser;
    coordinateSectionParser;
    connectivitySectionParser = new qb.ConnectivitySectionParser;
    bookkeepingSectionParser = new Wb.BookkeepingSectionParser;
    constructor(Q = !0, J = !0, Y = null, W = null) {
      super();
      this.coordinateSectionParser = new Yb.CoordinateSectionParser(Q, J, Y, W);
    }
    parsers() {
      return [
        this.titleSectionParser,
        this.primaryStructureSectionParser,
        this.heterogenSectionParser,
        this.secondaryStructureSectionParser,
        this.connectivityAnnotationSectionParser,
        this.miscellaneousFeaturesSectionParser,
        this.crystallographicAndCoordinateTransformationSectionParser,
        this.coordinateSectionParser,
        this.connectivitySectionParser,
        this.bookkeepingSectionParser
      ];
    }
    parse() {
      return new HU(this.titleSectionParser.parse(), this.primaryStructureSectionParser.parse(), this.heterogenSectionParser.parse(), this.secondaryStructureSectionParser.parse(), this.connectivityAnnotationSectionParser.parse(), this.miscellaneousFeaturesSectionParser.parse(), this.crystallographicAndCoordinateTransformationSectionParser.parse(), this.coordinateSectionParser.parse(), this.connectivitySectionParser.parse(), this.bookkeepingSectionParser.parse());
    }
  }
  CR.PdbParser = BR;
});

// node_modules/pdb-parser-js/dist/index.js
var gR = $6((j0) => {
  Object.defineProperty(j0, "__esModule", { value: !0 });
  j0.ConnectivitySectionParser = j0.HetatmParser = j0.AnisouParser = j0.AtomParser = j0.CoordinateSectionParser = j0.MtrixParser = j0.ScaleParser = j0.OrigxParser = j0.Cryst1Parser = j0.CrystallographicAndCoordinateTransformationSectionParser = j0.SiteParser = j0.MiscellaneousFeaturesSectionParser = j0.CispepParser = j0.LinkParser = j0.SsbondParser = j0.ConnectivityAnnotationSectionParser = j0.SheetParser = j0.HelixParser = j0.SecondaryStructureSectionParser = j0.FormulParser = j0.HetsynParser = j0.HetnamParser = j0.HetParser = j0.HeterogenSectionParser = j0.SeqresParser = j0.Dbref2Parser = j0.Dbref1Parser = j0.ModresParser = j0.SeqadvParser = j0.DbrefParser = j0.PrimaryStructureSectionParser = j0.Remark470Parser = j0.Remark465Parser = j0.RemarkParser = j0.SprsdeParser = j0.RevdatParser = j0.AuthorParser = j0.MdltypParser = j0.NummdlParser = j0.ExpdtaParser = j0.KeywdsParser = j0.SourceParser = j0.CompndParser = j0.CaveatParser = j0.SplitParser = j0.TitleParser = j0.ObslteParser = j0.HeaderParser = j0.TitleSectionParser = j0.PdbParser = void 0;
  j0.MasterParser = j0.BookkeepingSectionParser = j0.ConectParser = void 0;
  var Gb = SR();
  Object.defineProperty(j0, "PdbParser", { enumerable: !0, get: function() {
    return Gb.PdbParser;
  } });
  var IR = KU();
  Object.defineProperty(j0, "BookkeepingSectionParser", { enumerable: !0, get: function() {
    return IR.BookkeepingSectionParser;
  } });
  Object.defineProperty(j0, "MasterParser", { enumerable: !0, get: function() {
    return IR.MasterParser;
  } });
  var _R = qU();
  Object.defineProperty(j0, "ConectParser", { enumerable: !0, get: function() {
    return _R.ConectParser;
  } });
  Object.defineProperty(j0, "ConnectivitySectionParser", { enumerable: !0, get: function() {
    return _R.ConnectivitySectionParser;
  } });
  var Y7 = uF();
  Object.defineProperty(j0, "CispepParser", { enumerable: !0, get: function() {
    return Y7.CispepParser;
  } });
  Object.defineProperty(j0, "ConnectivityAnnotationSectionParser", { enumerable: !0, get: function() {
    return Y7.ConnectivityAnnotationSectionParser;
  } });
  Object.defineProperty(j0, "LinkParser", { enumerable: !0, get: function() {
    return Y7.LinkParser;
  } });
  Object.defineProperty(j0, "SsbondParser", { enumerable: !0, get: function() {
    return Y7.SsbondParser;
  } });
  var q7 = $U();
  Object.defineProperty(j0, "AnisouParser", { enumerable: !0, get: function() {
    return q7.AnisouParser;
  } });
  Object.defineProperty(j0, "AtomParser", { enumerable: !0, get: function() {
    return q7.AtomParser;
  } });
  Object.defineProperty(j0, "CoordinateSectionParser", { enumerable: !0, get: function() {
    return q7.CoordinateSectionParser;
  } });
  Object.defineProperty(j0, "HetatmParser", { enumerable: !0, get: function() {
    return q7.HetatmParser;
  } });
  var NK = tF();
  Object.defineProperty(j0, "Cryst1Parser", { enumerable: !0, get: function() {
    return NK.Cryst1Parser;
  } });
  Object.defineProperty(j0, "CrystallographicAndCoordinateTransformationSectionParser", { enumerable: !0, get: function() {
    return NK.CrystallographicAndCoordinateTransformationSectionParser;
  } });
  Object.defineProperty(j0, "MtrixParser", { enumerable: !0, get: function() {
    return NK.MtrixParser;
  } });
  Object.defineProperty(j0, "OrigxParser", { enumerable: !0, get: function() {
    return NK.OrigxParser;
  } });
  Object.defineProperty(j0, "ScaleParser", { enumerable: !0, get: function() {
    return NK.ScaleParser;
  } });
  var EK = gF();
  Object.defineProperty(j0, "FormulParser", { enumerable: !0, get: function() {
    return EK.FormulParser;
  } });
  Object.defineProperty(j0, "HeterogenSectionParser", { enumerable: !0, get: function() {
    return EK.HeterogenSectionParser;
  } });
  Object.defineProperty(j0, "HetnamParser", { enumerable: !0, get: function() {
    return EK.HetnamParser;
  } });
  Object.defineProperty(j0, "HetParser", { enumerable: !0, get: function() {
    return EK.HetParser;
  } });
  Object.defineProperty(j0, "HetsynParser", { enumerable: !0, get: function() {
    return EK.HetsynParser;
  } });
  var TR = dF();
  Object.defineProperty(j0, "MiscellaneousFeaturesSectionParser", { enumerable: !0, get: function() {
    return TR.MiscellaneousFeaturesSectionParser;
  } });
  Object.defineProperty(j0, "SiteParser", { enumerable: !0, get: function() {
    return TR.SiteParser;
  } });
  var n$ = VF();
  Object.defineProperty(j0, "Dbref1Parser", { enumerable: !0, get: function() {
    return n$.Dbref1Parser;
  } });
  Object.defineProperty(j0, "Dbref2Parser", { enumerable: !0, get: function() {
    return n$.Dbref2Parser;
  } });
  Object.defineProperty(j0, "DbrefParser", { enumerable: !0, get: function() {
    return n$.DbrefParser;
  } });
  Object.defineProperty(j0, "ModresParser", { enumerable: !0, get: function() {
    return n$.ModresParser;
  } });
  Object.defineProperty(j0, "PrimaryStructureSectionParser", { enumerable: !0, get: function() {
    return n$.PrimaryStructureSectionParser;
  } });
  Object.defineProperty(j0, "SeqadvParser", { enumerable: !0, get: function() {
    return n$.SeqadvParser;
  } });
  Object.defineProperty(j0, "SeqresParser", { enumerable: !0, get: function() {
    return n$.SeqresParser;
  } });
  var GU = yF();
  Object.defineProperty(j0, "HelixParser", { enumerable: !0, get: function() {
    return GU.HelixParser;
  } });
  Object.defineProperty(j0, "SecondaryStructureSectionParser", { enumerable: !0, get: function() {
    return GU.SecondaryStructureSectionParser;
  } });
  Object.defineProperty(j0, "SheetParser", { enumerable: !0, get: function() {
    return GU.SheetParser;
  } });
  var D8 = MF();
  Object.defineProperty(j0, "AuthorParser", { enumerable: !0, get: function() {
    return D8.AuthorParser;
  } });
  Object.defineProperty(j0, "CaveatParser", { enumerable: !0, get: function() {
    return D8.CaveatParser;
  } });
  Object.defineProperty(j0, "CompndParser", { enumerable: !0, get: function() {
    return D8.CompndParser;
  } });
  Object.defineProperty(j0, "ExpdtaParser", { enumerable: !0, get: function() {
    return D8.ExpdtaParser;
  } });
  Object.defineProperty(j0, "HeaderParser", { enumerable: !0, get: function() {
    return D8.HeaderParser;
  } });
  Object.defineProperty(j0, "KeywdsParser", { enumerable: !0, get: function() {
    return D8.KeywdsParser;
  } });
  Object.defineProperty(j0, "MdltypParser", { enumerable: !0, get: function() {
    return D8.MdltypParser;
  } });
  Object.defineProperty(j0, "NummdlParser", { enumerable: !0, get: function() {
    return D8.NummdlParser;
  } });
  Object.defineProperty(j0, "ObslteParser", { enumerable: !0, get: function() {
    return D8.ObslteParser;
  } });
  Object.defineProperty(j0, "Remark465Parser", { enumerable: !0, get: function() {
    return D8.Remark465Parser;
  } });
  Object.defineProperty(j0, "Remark470Parser", { enumerable: !0, get: function() {
    return D8.Remark470Parser;
  } });
  Object.defineProperty(j0, "RemarkParser", { enumerable: !0, get: function() {
    return D8.RemarkParser;
  } });
  Object.defineProperty(j0, "RevdatParser", { enumerable: !0, get: function() {
    return D8.RevdatParser;
  } });
  Object.defineProperty(j0, "SourceParser", { enumerable: !0, get: function() {
    return D8.SourceParser;
  } });
  Object.defineProperty(j0, "SplitParser", { enumerable: !0, get: function() {
    return D8.SplitParser;
  } });
  Object.defineProperty(j0, "SprsdeParser", { enumerable: !0, get: function() {
    return D8.SprsdeParser;
  } });
  Object.defineProperty(j0, "TitleParser", { enumerable: !0, get: function() {
    return D8.TitleParser;
  } });
  Object.defineProperty(j0, "TitleSectionParser", { enumerable: !0, get: function() {
    return D8.TitleSectionParser;
  } });
});

// src/index.tsx
var H7 = D6(LQ(), 1), aR = D6(Cw(), 1);

// node_modules/streamlit-component-lib/dist/StreamlitReact.js
var lD = D6(vw(), 1), v$ = D6(nw(), 1);

// node_modules/tslib/tslib.es6.mjs
function ow(Q, J) {
  var Y = {};
  for (var W in Q)
    if (Object.prototype.hasOwnProperty.call(Q, W) && J.indexOf(W) < 0)
      Y[W] = Q[W];
  if (Q != null && typeof Object.getOwnPropertySymbols === "function") {
    for (var K = 0, W = Object.getOwnPropertySymbols(Q);K < W.length; K++)
      if (J.indexOf(W[K]) < 0 && Object.prototype.propertyIsEnumerable.call(Q, W[K]))
        Y[W[K]] = Q[W[K]];
  }
  return Y;
}
function U0(Q, J, Y, W) {
  function K(z) {
    return z instanceof Y ? z : new Y(function(N) {
      N(z);
    });
  }
  return new (Y || (Y = Promise))(function(z, N) {
    function F(D) {
      try {
        w(W.next(D));
      } catch (R) {
        N(R);
      }
    }
    function L(D) {
      try {
        w(W.throw(D));
      } catch (R) {
        N(R);
      }
    }
    function w(D) {
      D.done ? z(D.value) : K(D.value).then(F, L);
    }
    w((W = W.apply(Q, J || [])).next());
  });
}
function sw(Q) {
  var J = typeof Symbol === "function" && Symbol.iterator, Y = J && Q[J], W = 0;
  if (Y)
    return Y.call(Q);
  if (Q && typeof Q.length === "number")
    return {
      next: function() {
        if (Q && W >= Q.length)
          Q = void 0;
        return { value: Q && Q[W++], done: !Q };
      }
    };
  throw new TypeError(J ? "Object is not iterable." : "Symbol.iterator is not defined.");
}
function i0(Q) {
  return this instanceof i0 ? (this.v = Q, this) : new i0(Q);
}
function eQ(Q, J, Y) {
  if (!Symbol.asyncIterator)
    throw new TypeError("Symbol.asyncIterator is not defined.");
  var W = Y.apply(Q, J || []), K, z = [];
  return K = Object.create((typeof AsyncIterator === "function" ? AsyncIterator : Object).prototype), F("next"), F("throw"), F("return", N), K[Symbol.asyncIterator] = function() {
    return this;
  }, K;
  function N(g) {
    return function(s) {
      return Promise.resolve(s).then(g, R);
    };
  }
  function F(g, s) {
    if (W[g]) {
      if (K[g] = function(i) {
        return new Promise(function(F0, r) {
          z.push([g, i, F0, r]) > 1 || L(g, i);
        });
      }, s)
        K[g] = s(K[g]);
    }
  }
  function L(g, s) {
    try {
      w(W[g](s));
    } catch (i) {
      V(z[0][3], i);
    }
  }
  function w(g) {
    g.value instanceof i0 ? Promise.resolve(g.value.v).then(D, R) : V(z[0][2], g);
  }
  function D(g) {
    L("next", g);
  }
  function R(g) {
    L("throw", g);
  }
  function V(g, s) {
    if (g(s), z.shift(), z.length)
      L(z[0][0], z[0][1]);
  }
}
function iY(Q) {
  var J, Y;
  return J = {}, W("next"), W("throw", function(K) {
    throw K;
  }), W("return"), J[Symbol.iterator] = function() {
    return this;
  }, J;
  function W(K, z) {
    J[K] = Q[K] ? function(N) {
      return (Y = !Y) ? { value: i0(Q[K](N)), done: !1 } : z ? z(N) : N;
    } : z;
  }
}
function ZX(Q) {
  if (!Symbol.asyncIterator)
    throw new TypeError("Symbol.asyncIterator is not defined.");
  var J = Q[Symbol.asyncIterator], Y;
  return J ? J.call(Q) : (Q = typeof sw === "function" ? sw(Q) : Q[Symbol.iterator](), Y = {}, W("next"), W("throw"), W("return"), Y[Symbol.asyncIterator] = function() {
    return this;
  }, Y);
  function W(z) {
    Y[z] = Q[z] && function(N) {
      return new Promise(function(F, L) {
        N = Q[z](N), K(F, L, N.done, N.value);
      });
    };
  }
  function K(z, N, F, L) {
    Promise.resolve(L).then(function(w) {
      z({ value: w, done: F });
    }, N);
  }
}

// node_modules/apache-arrow/util/buffer.mjs
var BN = {};
sY(BN, {
  toUint8ClampedArrayIterator: () => Yv,
  toUint8ClampedArrayAsyncIterator: () => Ev,
  toUint8ClampedArray: () => ix,
  toUint8ArrayIterator: () => kN,
  toUint8ArrayAsyncIterator: () => RN,
  toUint8Array: () => n0,
  toUint32ArrayIterator: () => Xv,
  toUint32ArrayAsyncIterator: () => Gv,
  toUint32Array: () => sx,
  toUint16ArrayIterator: () => Zv,
  toUint16ArrayAsyncIterator: () => Hv,
  toUint16Array: () => nx,
  toInt8ArrayIterator: () => tx,
  toInt8ArrayAsyncIterator: () => qv,
  toInt8Array: () => px,
  toInt32ArrayIterator: () => Qv,
  toInt32ArrayAsyncIterator: () => Kv,
  toInt32Array: () => k$,
  toInt16ArrayIterator: () => ex,
  toInt16ArrayAsyncIterator: () => Wv,
  toInt16Array: () => dx,
  toFloat64ArrayIterator: () => $v,
  toFloat64ArrayAsyncIterator: () => Nv,
  toFloat64Array: () => rx,
  toFloat32ArrayIterator: () => Jv,
  toFloat32ArrayAsyncIterator: () => zv,
  toFloat32Array: () => ax,
  toBigUint64Array: () => ox,
  toBigInt64Array: () => lx,
  toArrayBufferViewIterator: () => hX,
  toArrayBufferViewAsyncIterator: () => JX,
  toArrayBufferView: () => G1,
  rebaseValueOffsets: () => M3,
  memcpy: () => tY,
  joinUint8Arrays: () => ZZ,
  compareArrayLike: () => jN
});

// node_modules/apache-arrow/util/utf8.mjs
var mx = new TextDecoder("utf-8"), O3 = (Q) => mx.decode(Q), bx = /* @__PURE__ */ new TextEncoder, WJ = (Q) => bx.encode(Q);

// node_modules/apache-arrow/util/compat.mjs
var [Xp, S5] = (() => {
  let Q = () => {
    throw new Error("BigInt is not available in this environment");
  };
  function J() {
    throw Q();
  }
  return J.asIntN = () => {
    throw Q();
  }, J.asUintN = () => {
    throw Q();
  }, typeof BigInt !== "undefined" ? [BigInt, !0] : [J, !1];
})(), [AZ, Jp] = (() => {
  let Q = () => {
    throw new Error("BigInt64Array is not available in this environment");
  };

  class J {
    static get BYTES_PER_ELEMENT() {
      return 8;
    }
    static of() {
      throw Q();
    }
    static from() {
      throw Q();
    }
    constructor() {
      throw Q();
    }
  }
  return typeof BigInt64Array !== "undefined" ? [BigInt64Array, !0] : [J, !1];
})(), [LZ, $p] = (() => {
  let Q = () => {
    throw new Error("BigUint64Array is not available in this environment");
  };

  class J {
    static get BYTES_PER_ELEMENT() {
      return 8;
    }
    static of() {
      throw Q();
    }
    static from() {
      throw Q();
    }
    constructor() {
      throw Q();
    }
  }
  return typeof BigUint64Array !== "undefined" ? [BigUint64Array, !0] : [J, !1];
})();
var ux = (Q) => typeof Q === "number", aw = (Q) => typeof Q === "boolean", X8 = (Q) => typeof Q === "function", OQ = (Q) => Q != null && Object(Q) === Q, QZ = (Q) => {
  return OQ(Q) && X8(Q.then);
};
var XX = (Q) => {
  return OQ(Q) && X8(Q[Symbol.iterator]);
}, OZ = (Q) => {
  return OQ(Q) && X8(Q[Symbol.asyncIterator]);
}, I5 = (Q) => {
  return OQ(Q) && OQ(Q.schema);
};
var _5 = (Q) => {
  return OQ(Q) && "done" in Q && "value" in Q;
};
var T5 = (Q) => {
  return OQ(Q) && X8(Q.stat) && ux(Q.fd);
};
var g5 = (Q) => {
  return OQ(Q) && w3(Q.body);
}, x5 = (Q) => ("_getDOMStream" in Q) && ("_getNodeStream" in Q), rw = (Q) => {
  return OQ(Q) && X8(Q.abort) && X8(Q.getWriter) && !x5(Q);
}, w3 = (Q) => {
  return OQ(Q) && X8(Q.cancel) && X8(Q.getReader) && !x5(Q);
}, iw = (Q) => {
  return OQ(Q) && X8(Q.end) && X8(Q.write) && aw(Q.writable) && !x5(Q);
}, v5 = (Q) => {
  return OQ(Q) && X8(Q.read) && X8(Q.pipe) && aw(Q.readable) && !x5(Q);
}, tw = (Q) => {
  return OQ(Q) && X8(Q.clear) && X8(Q.bytes) && X8(Q.position) && X8(Q.setPosition) && X8(Q.capacity) && X8(Q.getBufferIdentifier) && X8(Q.createLong);
};

// node_modules/apache-arrow/util/buffer.mjs
var DN = typeof SharedArrayBuffer !== "undefined" ? SharedArrayBuffer : ArrayBuffer;
function cx(Q) {
  let J = Q[0] ? [Q[0]] : [], Y, W, K, z;
  for (let N, F, L = 0, w = 0, D = Q.length;++L < D; ) {
    if (N = J[w], F = Q[L], !N || !F || N.buffer !== F.buffer || F.byteOffset < N.byteOffset) {
      F && (J[++w] = F);
      continue;
    }
    if ({ byteOffset: Y, byteLength: K } = N, { byteOffset: W, byteLength: z } = F, Y + K < W || W + z < Y) {
      F && (J[++w] = F);
      continue;
    }
    J[w] = new Uint8Array(N.buffer, Y, W - Y + z);
  }
  return J;
}
function tY(Q, J, Y = 0, W = J.byteLength) {
  let K = Q.byteLength, z = new Uint8Array(Q.buffer, Q.byteOffset, K), N = new Uint8Array(J.buffer, J.byteOffset, Math.min(W, K));
  return z.set(N, Y), Q;
}
function ZZ(Q, J) {
  let Y = cx(Q), W = Y.reduce((D, R) => D + R.byteLength, 0), K, z, N, F = 0, L = -1, w = Math.min(J || Number.POSITIVE_INFINITY, W);
  for (let D = Y.length;++L < D; ) {
    if (K = Y[L], z = K.subarray(0, Math.min(K.length, w - F)), w <= F + z.length) {
      if (z.length < K.length)
        Y[L] = K.subarray(z.length);
      else if (z.length === K.length)
        L++;
      N ? tY(N, z, F) : N = z;
      break;
    }
    tY(N || (N = new Uint8Array(w)), z, F), F += z.length;
  }
  return [N || new Uint8Array(0), Y.slice(L), W - (N ? N.byteLength : 0)];
}
function G1(Q, J) {
  let Y = _5(J) ? J.value : J;
  if (Y instanceof Q) {
    if (Q === Uint8Array)
      return new Q(Y.buffer, Y.byteOffset, Y.byteLength);
    return Y;
  }
  if (!Y)
    return new Q(0);
  if (typeof Y === "string")
    Y = WJ(Y);
  if (Y instanceof ArrayBuffer)
    return new Q(Y);
  if (Y instanceof DN)
    return new Q(Y);
  if (tw(Y))
    return G1(Q, Y.bytes());
  return !ArrayBuffer.isView(Y) ? Q.from(Y) : Y.byteLength <= 0 ? new Q(0) : new Q(Y.buffer, Y.byteOffset, Y.byteLength / Q.BYTES_PER_ELEMENT);
}
var px = (Q) => G1(Int8Array, Q), dx = (Q) => G1(Int16Array, Q), k$ = (Q) => G1(Int32Array, Q), lx = (Q) => G1(AZ, Q), n0 = (Q) => G1(Uint8Array, Q), nx = (Q) => G1(Uint16Array, Q), sx = (Q) => G1(Uint32Array, Q), ox = (Q) => G1(LZ, Q), ax = (Q) => G1(Float32Array, Q), rx = (Q) => G1(Float64Array, Q), ix = (Q) => G1(Uint8ClampedArray, Q), MN = (Q) => {
  return Q.next(), Q;
};
function* hX(Q, J) {
  let Y = function* (K) {
    yield K;
  }, W = typeof J === "string" ? Y(J) : ArrayBuffer.isView(J) ? Y(J) : J instanceof ArrayBuffer ? Y(J) : J instanceof DN ? Y(J) : !XX(J) ? Y(J) : J;
  return yield* MN(function* (K) {
    let z = null;
    do
      z = K.next(yield G1(Q, z));
    while (!z.done);
  }(W[Symbol.iterator]())), new Q;
}
var tx = (Q) => hX(Int8Array, Q), ex = (Q) => hX(Int16Array, Q), Qv = (Q) => hX(Int32Array, Q), kN = (Q) => hX(Uint8Array, Q), Zv = (Q) => hX(Uint16Array, Q), Xv = (Q) => hX(Uint32Array, Q), Jv = (Q) => hX(Float32Array, Q), $v = (Q) => hX(Float64Array, Q), Yv = (Q) => hX(Uint8ClampedArray, Q);
function JX(Q, J) {
  return eQ(this, arguments, function* Y() {
    if (QZ(J))
      return yield i0(yield i0(yield* iY(ZX(JX(Q, yield i0(J))))));
    let W = function(N) {
      return eQ(this, arguments, function* () {
        yield yield i0(yield i0(N));
      });
    }, K = function(N) {
      return eQ(this, arguments, function* () {
        yield i0(yield* iY(ZX(MN(function* (F) {
          let L = null;
          do
            L = F.next(yield L === null || L === void 0 ? void 0 : L.value);
          while (!L.done);
        }(N[Symbol.iterator]())))));
      });
    }, z = typeof J === "string" ? W(J) : ArrayBuffer.isView(J) ? W(J) : J instanceof ArrayBuffer ? W(J) : J instanceof DN ? W(J) : XX(J) ? K(J) : !OZ(J) ? W(J) : J;
    return yield i0(yield* iY(ZX(MN(function(N) {
      return eQ(this, arguments, function* () {
        let F = null;
        do
          F = yield i0(N.next(yield yield i0(G1(Q, F))));
        while (!F.done);
      });
    }(z[Symbol.asyncIterator]()))))), yield i0(new Q);
  });
}
var qv = (Q) => JX(Int8Array, Q), Wv = (Q) => JX(Int16Array, Q), Kv = (Q) => JX(Int32Array, Q), RN = (Q) => JX(Uint8Array, Q), Hv = (Q) => JX(Uint16Array, Q), Gv = (Q) => JX(Uint32Array, Q), zv = (Q) => JX(Float32Array, Q), Nv = (Q) => JX(Float64Array, Q), Ev = (Q) => JX(Uint8ClampedArray, Q);
function M3(Q, J, Y) {
  if (Q !== 0) {
    Y = Y.slice(0, J + 1);
    for (let W = -1;++W <= J; )
      Y[W] += Q;
  }
  return Y;
}
function jN(Q, J) {
  let Y = 0, W = Q.length;
  if (W !== J.length)
    return !1;
  if (W > 0)
    do
      if (Q[Y] !== J[Y])
        return !1;
    while (++Y < W);
  return !0;
}

// node_modules/apache-arrow/io/adapters.mjs
var y8 = {
  fromIterable(Q) {
    return h5(Fv(Q));
  },
  fromAsyncIterable(Q) {
    return h5(Uv(Q));
  },
  fromDOMStream(Q) {
    return h5(Pv(Q));
  },
  fromNodeStream(Q) {
    return h5(Av(Q));
  },
  toDOMStream(Q, J) {
    throw new Error('"toDOMStream" not available in this environment');
  },
  toNodeStream(Q, J) {
    throw new Error('"toNodeStream" not available in this environment');
  }
}, h5 = (Q) => {
  return Q.next(), Q;
};
function* Fv(Q) {
  let J, Y = !1, W = [], K, z, N, F = 0;
  function L() {
    if (z === "peek")
      return ZZ(W, N)[0];
    return [K, W, F] = ZZ(W, N), K;
  }
  ({ cmd: z, size: N } = yield null);
  let w = kN(Q)[Symbol.iterator]();
  try {
    do {
      if ({ done: J, value: K } = Number.isNaN(N - F) ? w.next() : w.next(N - F), !J && K.byteLength > 0)
        W.push(K), F += K.byteLength;
      if (J || N <= F)
        do
          ({ cmd: z, size: N } = yield L());
        while (N < F);
    } while (!J);
  } catch (D) {
    (Y = !0) && typeof w.throw === "function" && w.throw(D);
  } finally {
    Y === !1 && typeof w.return === "function" && w.return(null);
  }
  return null;
}
function Uv(Q) {
  return eQ(this, arguments, function* J() {
    let Y, W = !1, K = [], z, N, F, L = 0;
    function w() {
      if (N === "peek")
        return ZZ(K, F)[0];
      return [z, K, L] = ZZ(K, F), z;
    }
    ({ cmd: N, size: F } = yield yield i0(null));
    let D = RN(Q)[Symbol.asyncIterator]();
    try {
      do {
        if ({ done: Y, value: z } = Number.isNaN(F - L) ? yield i0(D.next()) : yield i0(D.next(F - L)), !Y && z.byteLength > 0)
          K.push(z), L += z.byteLength;
        if (Y || F <= L)
          do
            ({ cmd: N, size: F } = yield yield i0(w()));
          while (F < L);
      } while (!Y);
    } catch (R) {
      (W = !0) && typeof D.throw === "function" && (yield i0(D.throw(R)));
    } finally {
      W === !1 && typeof D.return === "function" && (yield i0(D.return(new Uint8Array(0))));
    }
    return yield i0(null);
  });
}
function Pv(Q) {
  return eQ(this, arguments, function* J() {
    let Y = !1, W = !1, K = [], z, N, F, L = 0;
    function w() {
      if (N === "peek")
        return ZZ(K, F)[0];
      return [z, K, L] = ZZ(K, F), z;
    }
    ({ cmd: N, size: F } = yield yield i0(null));
    let D = new ew(Q);
    try {
      do {
        if ({ done: Y, value: z } = Number.isNaN(F - L) ? yield i0(D.read()) : yield i0(D.read(F - L)), !Y && z.byteLength > 0)
          K.push(n0(z)), L += z.byteLength;
        if (Y || F <= L)
          do
            ({ cmd: N, size: F } = yield yield i0(w()));
          while (F < L);
      } while (!Y);
    } catch (R) {
      (W = !0) && (yield i0(D.cancel(R)));
    } finally {
      W === !1 ? yield i0(D.cancel()) : Q.locked && D.releaseLock();
    }
    return yield i0(null);
  });
}

class ew {
  constructor(Q) {
    this.source = Q, this.reader = null, this.reader = this.source.getReader(), this.reader.closed.catch(() => {});
  }
  get closed() {
    return this.reader ? this.reader.closed.catch(() => {}) : Promise.resolve();
  }
  releaseLock() {
    if (this.reader)
      this.reader.releaseLock();
    this.reader = null;
  }
  cancel(Q) {
    return U0(this, void 0, void 0, function* () {
      let { reader: J, source: Y } = this;
      J && (yield J.cancel(Q).catch(() => {})), Y && (Y.locked && this.releaseLock());
    });
  }
  read(Q) {
    return U0(this, void 0, void 0, function* () {
      if (Q === 0)
        return { done: this.reader == null, value: new Uint8Array(0) };
      let J = yield this.reader.read();
      return !J.done && (J.value = n0(J)), J;
    });
  }
}
var CN = (Q, J) => {
  let Y = (K) => W([J, K]), W;
  return [J, Y, new Promise((K) => (W = K) && Q.once(J, Y))];
};
function Av(Q) {
  return eQ(this, arguments, function* J() {
    let Y = [], W = "error", K = !1, z = null, N, F, L = 0, w = [], D;
    function R() {
      if (N === "peek")
        return ZZ(w, F)[0];
      return [D, w, L] = ZZ(w, F), D;
    }
    if ({ cmd: N, size: F } = yield yield i0(null), Q.isTTY)
      return yield yield i0(new Uint8Array(0)), yield i0(null);
    try {
      Y[0] = CN(Q, "end"), Y[1] = CN(Q, "error");
      do {
        if (Y[2] = CN(Q, "readable"), [W, z] = yield i0(Promise.race(Y.map((g) => g[2]))), W === "error")
          break;
        if (!(K = W === "end")) {
          if (!Number.isFinite(F - L))
            D = n0(Q.read());
          else if (D = n0(Q.read(F - L)), D.byteLength < F - L)
            D = n0(Q.read());
          if (D.byteLength > 0)
            w.push(D), L += D.byteLength;
        }
        if (K || F <= L)
          do
            ({ cmd: N, size: F } = yield yield i0(R()));
          while (F < L);
      } while (!K);
    } finally {
      yield i0(V(Y, W === "error" ? z : null));
    }
    return yield i0(null);
    function V(g, s) {
      return D = w = null, new Promise((i, F0) => {
        for (let [r, J0] of g)
          Q.off(r, J0);
        try {
          let r = Q.destroy;
          r && r.call(Q, s), s = void 0;
        } catch (r) {
          s = r || s;
        } finally {
          s != null ? F0(s) : i();
        }
      });
    }
  });
}

// node_modules/apache-arrow/enum.mjs
var A8;
(function(Q) {
  Q[Q.V1 = 0] = "V1", Q[Q.V2 = 1] = "V2", Q[Q.V3 = 2] = "V3", Q[Q.V4 = 3] = "V4", Q[Q.V5 = 4] = "V5";
})(A8 || (A8 = {}));
var k6;
(function(Q) {
  Q[Q.Sparse = 0] = "Sparse", Q[Q.Dense = 1] = "Dense";
})(k6 || (k6 = {}));
var K6;
(function(Q) {
  Q[Q.HALF = 0] = "HALF", Q[Q.SINGLE = 1] = "SINGLE", Q[Q.DOUBLE = 2] = "DOUBLE";
})(K6 || (K6 = {}));
var f8;
(function(Q) {
  Q[Q.DAY = 0] = "DAY", Q[Q.MILLISECOND = 1] = "MILLISECOND";
})(f8 || (f8 = {}));
var F1;
(function(Q) {
  Q[Q.SECOND = 0] = "SECOND", Q[Q.MILLISECOND = 1] = "MILLISECOND", Q[Q.MICROSECOND = 2] = "MICROSECOND", Q[Q.NANOSECOND = 3] = "NANOSECOND";
})(F1 || (F1 = {}));
var wQ;
(function(Q) {
  Q[Q.YEAR_MONTH = 0] = "YEAR_MONTH", Q[Q.DAY_TIME = 1] = "DAY_TIME", Q[Q.MONTH_DAY_NANO = 2] = "MONTH_DAY_NANO";
})(wQ || (wQ = {}));
var B1;
(function(Q) {
  Q[Q.NONE = 0] = "NONE", Q[Q.Schema = 1] = "Schema", Q[Q.DictionaryBatch = 2] = "DictionaryBatch", Q[Q.RecordBatch = 3] = "RecordBatch", Q[Q.Tensor = 4] = "Tensor", Q[Q.SparseTensor = 5] = "SparseTensor";
})(B1 || (B1 = {}));
var I;
(function(Q) {
  Q[Q.NONE = 0] = "NONE", Q[Q.Null = 1] = "Null", Q[Q.Int = 2] = "Int", Q[Q.Float = 3] = "Float", Q[Q.Binary = 4] = "Binary", Q[Q.Utf8 = 5] = "Utf8", Q[Q.Bool = 6] = "Bool", Q[Q.Decimal = 7] = "Decimal", Q[Q.Date = 8] = "Date", Q[Q.Time = 9] = "Time", Q[Q.Timestamp = 10] = "Timestamp", Q[Q.Interval = 11] = "Interval", Q[Q.List = 12] = "List", Q[Q.Struct = 13] = "Struct", Q[Q.Union = 14] = "Union", Q[Q.FixedSizeBinary = 15] = "FixedSizeBinary", Q[Q.FixedSizeList = 16] = "FixedSizeList", Q[Q.Map = 17] = "Map", Q[Q.Dictionary = -1] = "Dictionary", Q[Q.Int8 = -2] = "Int8", Q[Q.Int16 = -3] = "Int16", Q[Q.Int32 = -4] = "Int32", Q[Q.Int64 = -5] = "Int64", Q[Q.Uint8 = -6] = "Uint8", Q[Q.Uint16 = -7] = "Uint16", Q[Q.Uint32 = -8] = "Uint32", Q[Q.Uint64 = -9] = "Uint64", Q[Q.Float16 = -10] = "Float16", Q[Q.Float32 = -11] = "Float32", Q[Q.Float64 = -12] = "Float64", Q[Q.DateDay = -13] = "DateDay", Q[Q.DateMillisecond = -14] = "DateMillisecond", Q[Q.TimestampSecond = -15] = "TimestampSecond", Q[Q.TimestampMillisecond = -16] = "TimestampMillisecond", Q[Q.TimestampMicrosecond = -17] = "TimestampMicrosecond", Q[Q.TimestampNanosecond = -18] = "TimestampNanosecond", Q[Q.TimeSecond = -19] = "TimeSecond", Q[Q.TimeMillisecond = -20] = "TimeMillisecond", Q[Q.TimeMicrosecond = -21] = "TimeMicrosecond", Q[Q.TimeNanosecond = -22] = "TimeNanosecond", Q[Q.DenseUnion = -23] = "DenseUnion", Q[Q.SparseUnion = -24] = "SparseUnion", Q[Q.IntervalDayTime = -25] = "IntervalDayTime", Q[Q.IntervalYearMonth = -26] = "IntervalYearMonth";
})(I || (I = {}));
var wZ;
(function(Q) {
  Q[Q.OFFSET = 0] = "OFFSET", Q[Q.DATA = 1] = "DATA", Q[Q.VALIDITY = 2] = "VALIDITY", Q[Q.TYPE = 3] = "TYPE";
})(wZ || (wZ = {}));

// node_modules/apache-arrow/util/vector.mjs
var rN = {};
sY(rN, {
  createElementComparator: () => LJ,
  clampRange: () => j3,
  clampIndex: () => Kh
});

// node_modules/apache-arrow/util/pretty.mjs
var Lv = void 0;
function $X(Q) {
  if (Q === null)
    return "null";
  if (Q === Lv)
    return "undefined";
  switch (typeof Q) {
    case "number":
      return `${Q}`;
    case "bigint":
      return `${Q}`;
    case "string":
      return `"${Q}"`;
  }
  if (typeof Q[Symbol.toPrimitive] === "function")
    return Q[Symbol.toPrimitive]("string");
  if (ArrayBuffer.isView(Q)) {
    if (Q instanceof AZ || Q instanceof LZ)
      return `[${[...Q].map((J) => $X(J))}]`;
    return `[${Q}]`;
  }
  return ArrayBuffer.isView(Q) ? `[${Q}]` : JSON.stringify(Q, (J, Y) => typeof Y === "bigint" ? `${Y}` : Y);
}

// node_modules/apache-arrow/util/bn.mjs
var SN = {};
sY(SN, {
  isArrowBigNumSymbol: () => QM,
  bignumToString: () => KJ,
  bignumToBigInt: () => y5,
  BN: () => k3
});
var QM = Symbol.for("isArrowBigNum");
function YX(Q, ...J) {
  if (J.length === 0)
    return Object.setPrototypeOf(G1(this.TypedArray, Q), this.constructor.prototype);
  return Object.setPrototypeOf(new this.TypedArray(Q, ...J), this.constructor.prototype);
}
YX.prototype[QM] = !0;
YX.prototype.toJSON = function() {
  return `"${KJ(this)}"`;
};
YX.prototype.valueOf = function() {
  return ZM(this);
};
YX.prototype.toString = function() {
  return KJ(this);
};
YX.prototype[Symbol.toPrimitive] = function(Q = "default") {
  switch (Q) {
    case "number":
      return ZM(this);
    case "string":
      return KJ(this);
    case "default":
      return y5(this);
  }
  return KJ(this);
};
function eY(...Q) {
  return YX.apply(this, Q);
}
function Qq(...Q) {
  return YX.apply(this, Q);
}
function D3(...Q) {
  return YX.apply(this, Q);
}
Object.setPrototypeOf(eY.prototype, Object.create(Int32Array.prototype));
Object.setPrototypeOf(Qq.prototype, Object.create(Uint32Array.prototype));
Object.setPrototypeOf(D3.prototype, Object.create(Uint32Array.prototype));
Object.assign(eY.prototype, YX.prototype, { constructor: eY, signed: !0, TypedArray: Int32Array, BigIntArray: AZ });
Object.assign(Qq.prototype, YX.prototype, { constructor: Qq, signed: !1, TypedArray: Uint32Array, BigIntArray: LZ });
Object.assign(D3.prototype, YX.prototype, { constructor: D3, signed: !0, TypedArray: Uint32Array, BigIntArray: LZ });
function ZM(Q) {
  let { buffer: J, byteOffset: Y, length: W, signed: K } = Q, z = new LZ(J, Y, W), N = K && z[z.length - 1] & BigInt(1) << BigInt(63), F = N ? BigInt(1) : BigInt(0), L = BigInt(0);
  if (!N)
    for (let w of z)
      F += w * (BigInt(1) << BigInt(32) * L++);
  else {
    for (let w of z)
      F += ~w * (BigInt(1) << BigInt(32) * L++);
    F *= BigInt(-1);
  }
  return F;
}
var KJ, y5;
if (!S5)
  KJ = VN, y5 = KJ;
else
  y5 = (Q) => Q.byteLength === 8 ? new Q.BigIntArray(Q.buffer, Q.byteOffset, 1)[0] : VN(Q), KJ = (Q) => Q.byteLength === 8 ? `${new Q.BigIntArray(Q.buffer, Q.byteOffset, 1)[0]}` : VN(Q);
function VN(Q) {
  let J = "", Y = new Uint32Array(2), W = new Uint16Array(Q.buffer, Q.byteOffset, Q.byteLength / 2), K = new Uint32Array((W = new Uint16Array(W).reverse()).buffer), z = -1, N = W.length - 1;
  do {
    for (Y[0] = W[z = 0];z < N; )
      W[z++] = Y[1] = Y[0] / 10, Y[0] = (Y[0] - Y[1] * 10 << 16) + W[z];
    W[z] = Y[1] = Y[0] / 10, Y[0] = Y[0] - Y[1] * 10, J = `${Y[0]}${J}`;
  } while (K[0] || K[1] || K[2] || K[3]);
  return J !== null && J !== void 0 ? J : "0";
}

class k3 {
  static new(Q, J) {
    switch (J) {
      case !0:
        return new eY(Q);
      case !1:
        return new Qq(Q);
    }
    switch (Q.constructor) {
      case Int8Array:
      case Int16Array:
      case Int32Array:
      case AZ:
        return new eY(Q);
    }
    if (Q.byteLength === 16)
      return new D3(Q);
    return new Qq(Q);
  }
  static signed(Q) {
    return new eY(Q);
  }
  static unsigned(Q) {
    return new Qq(Q);
  }
  static decimal(Q) {
    return new D3(Q);
  }
  constructor(Q, J) {
    return k3.new(Q, J);
  }
}

// node_modules/apache-arrow/type.mjs
var XM, JM, $M, YM, qM, WM, KM, HM, GM, zM, NM, EM, FM, UM, PM, AM, LM, OM, wM;

class C0 {
  static isNull(Q) {
    return (Q === null || Q === void 0 ? void 0 : Q.typeId) === I.Null;
  }
  static isInt(Q) {
    return (Q === null || Q === void 0 ? void 0 : Q.typeId) === I.Int;
  }
  static isFloat(Q) {
    return (Q === null || Q === void 0 ? void 0 : Q.typeId) === I.Float;
  }
  static isBinary(Q) {
    return (Q === null || Q === void 0 ? void 0 : Q.typeId) === I.Binary;
  }
  static isUtf8(Q) {
    return (Q === null || Q === void 0 ? void 0 : Q.typeId) === I.Utf8;
  }
  static isBool(Q) {
    return (Q === null || Q === void 0 ? void 0 : Q.typeId) === I.Bool;
  }
  static isDecimal(Q) {
    return (Q === null || Q === void 0 ? void 0 : Q.typeId) === I.Decimal;
  }
  static isDate(Q) {
    return (Q === null || Q === void 0 ? void 0 : Q.typeId) === I.Date;
  }
  static isTime(Q) {
    return (Q === null || Q === void 0 ? void 0 : Q.typeId) === I.Time;
  }
  static isTimestamp(Q) {
    return (Q === null || Q === void 0 ? void 0 : Q.typeId) === I.Timestamp;
  }
  static isInterval(Q) {
    return (Q === null || Q === void 0 ? void 0 : Q.typeId) === I.Interval;
  }
  static isList(Q) {
    return (Q === null || Q === void 0 ? void 0 : Q.typeId) === I.List;
  }
  static isStruct(Q) {
    return (Q === null || Q === void 0 ? void 0 : Q.typeId) === I.Struct;
  }
  static isUnion(Q) {
    return (Q === null || Q === void 0 ? void 0 : Q.typeId) === I.Union;
  }
  static isFixedSizeBinary(Q) {
    return (Q === null || Q === void 0 ? void 0 : Q.typeId) === I.FixedSizeBinary;
  }
  static isFixedSizeList(Q) {
    return (Q === null || Q === void 0 ? void 0 : Q.typeId) === I.FixedSizeList;
  }
  static isMap(Q) {
    return (Q === null || Q === void 0 ? void 0 : Q.typeId) === I.Map;
  }
  static isDictionary(Q) {
    return (Q === null || Q === void 0 ? void 0 : Q.typeId) === I.Dictionary;
  }
  static isDenseUnion(Q) {
    return C0.isUnion(Q) && Q.mode === k6.Dense;
  }
  static isSparseUnion(Q) {
    return C0.isUnion(Q) && Q.mode === k6.Sparse;
  }
  get typeId() {
    return I.NONE;
  }
}
XM = Symbol.toStringTag;
C0[XM] = ((Q) => {
  return Q.children = null, Q.ArrayType = Array, Q[Symbol.toStringTag] = "DataType";
})(C0.prototype);

class vQ extends C0 {
  toString() {
    return "Null";
  }
  get typeId() {
    return I.Null;
  }
}
JM = Symbol.toStringTag;
vQ[JM] = ((Q) => Q[Symbol.toStringTag] = "Null")(vQ.prototype);

class u6 extends C0 {
  constructor(Q, J) {
    super();
    this.isSigned = Q, this.bitWidth = J;
  }
  get typeId() {
    return I.Int;
  }
  get ArrayType() {
    switch (this.bitWidth) {
      case 8:
        return this.isSigned ? Int8Array : Uint8Array;
      case 16:
        return this.isSigned ? Int16Array : Uint16Array;
      case 32:
        return this.isSigned ? Int32Array : Uint32Array;
      case 64:
        return this.isSigned ? AZ : LZ;
    }
    throw new Error(`Unrecognized ${this[Symbol.toStringTag]} type`);
  }
  toString() {
    return `${this.isSigned ? "I" : "Ui"}nt${this.bitWidth}`;
  }
}
$M = Symbol.toStringTag;
u6[$M] = ((Q) => {
  return Q.isSigned = null, Q.bitWidth = null, Q[Symbol.toStringTag] = "Int";
})(u6.prototype);
class IN extends u6 {
  constructor() {
    super(!0, 8);
  }
  get ArrayType() {
    return Int8Array;
  }
}

class _N extends u6 {
  constructor() {
    super(!0, 16);
  }
  get ArrayType() {
    return Int16Array;
  }
}

class L4 extends u6 {
  constructor() {
    super(!0, 32);
  }
  get ArrayType() {
    return Int32Array;
  }
}

class TN extends u6 {
  constructor() {
    super(!0, 64);
  }
  get ArrayType() {
    return AZ;
  }
}

class gN extends u6 {
  constructor() {
    super(!1, 8);
  }
  get ArrayType() {
    return Uint8Array;
  }
}

class xN extends u6 {
  constructor() {
    super(!1, 16);
  }
  get ArrayType() {
    return Uint16Array;
  }
}

class vN extends u6 {
  constructor() {
    super(!1, 32);
  }
  get ArrayType() {
    return Uint32Array;
  }
}

class hN extends u6 {
  constructor() {
    super(!1, 64);
  }
  get ArrayType() {
    return LZ;
  }
}
Object.defineProperty(IN.prototype, "ArrayType", { value: Int8Array });
Object.defineProperty(_N.prototype, "ArrayType", { value: Int16Array });
Object.defineProperty(L4.prototype, "ArrayType", { value: Int32Array });
Object.defineProperty(TN.prototype, "ArrayType", { value: AZ });
Object.defineProperty(gN.prototype, "ArrayType", { value: Uint8Array });
Object.defineProperty(xN.prototype, "ArrayType", { value: Uint16Array });
Object.defineProperty(vN.prototype, "ArrayType", { value: Uint32Array });
Object.defineProperty(hN.prototype, "ArrayType", { value: LZ });

class XZ extends C0 {
  constructor(Q) {
    super();
    this.precision = Q;
  }
  get typeId() {
    return I.Float;
  }
  get ArrayType() {
    switch (this.precision) {
      case K6.HALF:
        return Uint16Array;
      case K6.SINGLE:
        return Float32Array;
      case K6.DOUBLE:
        return Float64Array;
    }
    throw new Error(`Unrecognized ${this[Symbol.toStringTag]} type`);
  }
  toString() {
    return `Float${this.precision << 5 || 16}`;
  }
}
YM = Symbol.toStringTag;
XZ[YM] = ((Q) => {
  return Q.precision = null, Q[Symbol.toStringTag] = "Float";
})(XZ.prototype);

class yN extends XZ {
  constructor() {
    super(K6.HALF);
  }
}

class fN extends XZ {
  constructor() {
    super(K6.SINGLE);
  }
}

class mN extends XZ {
  constructor() {
    super(K6.DOUBLE);
  }
}
Object.defineProperty(yN.prototype, "ArrayType", { value: Uint16Array });
Object.defineProperty(fN.prototype, "ArrayType", { value: Float32Array });
Object.defineProperty(mN.prototype, "ArrayType", { value: Float64Array });

class HJ extends C0 {
  constructor() {
    super();
  }
  get typeId() {
    return I.Binary;
  }
  toString() {
    return "Binary";
  }
}
qM = Symbol.toStringTag;
HJ[qM] = ((Q) => {
  return Q.ArrayType = Uint8Array, Q[Symbol.toStringTag] = "Binary";
})(HJ.prototype);

class GJ extends C0 {
  constructor() {
    super();
  }
  get typeId() {
    return I.Utf8;
  }
  toString() {
    return "Utf8";
  }
}
WM = Symbol.toStringTag;
GJ[WM] = ((Q) => {
  return Q.ArrayType = Uint8Array, Q[Symbol.toStringTag] = "Utf8";
})(GJ.prototype);

class zJ extends C0 {
  constructor() {
    super();
  }
  get typeId() {
    return I.Bool;
  }
  toString() {
    return "Bool";
  }
}
KM = Symbol.toStringTag;
zJ[KM] = ((Q) => {
  return Q.ArrayType = Uint8Array, Q[Symbol.toStringTag] = "Bool";
})(zJ.prototype);

class NJ extends C0 {
  constructor(Q, J, Y = 128) {
    super();
    this.scale = Q, this.precision = J, this.bitWidth = Y;
  }
  get typeId() {
    return I.Decimal;
  }
  toString() {
    return `Decimal[${this.precision}e${this.scale > 0 ? "+" : ""}${this.scale}]`;
  }
}
HM = Symbol.toStringTag;
NJ[HM] = ((Q) => {
  return Q.scale = null, Q.precision = null, Q.ArrayType = Uint32Array, Q[Symbol.toStringTag] = "Decimal";
})(NJ.prototype);

class EJ extends C0 {
  constructor(Q) {
    super();
    this.unit = Q;
  }
  get typeId() {
    return I.Date;
  }
  toString() {
    return `Date${(this.unit + 1) * 32}<${f8[this.unit]}>`;
  }
}
GM = Symbol.toStringTag;
EJ[GM] = ((Q) => {
  return Q.unit = null, Q.ArrayType = Int32Array, Q[Symbol.toStringTag] = "Date";
})(EJ.prototype);
class yX extends C0 {
  constructor(Q, J) {
    super();
    this.unit = Q, this.bitWidth = J;
  }
  get typeId() {
    return I.Time;
  }
  toString() {
    return `Time${this.bitWidth}<${F1[this.unit]}>`;
  }
  get ArrayType() {
    switch (this.bitWidth) {
      case 32:
        return Int32Array;
      case 64:
        return AZ;
    }
    throw new Error(`Unrecognized ${this[Symbol.toStringTag]} type`);
  }
}
zM = Symbol.toStringTag;
yX[zM] = ((Q) => {
  return Q.unit = null, Q.bitWidth = null, Q[Symbol.toStringTag] = "Time";
})(yX.prototype);
class FJ extends C0 {
  constructor(Q, J) {
    super();
    this.unit = Q, this.timezone = J;
  }
  get typeId() {
    return I.Timestamp;
  }
  toString() {
    return `Timestamp<${F1[this.unit]}${this.timezone ? `, ${this.timezone}` : ""}>`;
  }
}
NM = Symbol.toStringTag;
FJ[NM] = ((Q) => {
  return Q.unit = null, Q.timezone = null, Q.ArrayType = Int32Array, Q[Symbol.toStringTag] = "Timestamp";
})(FJ.prototype);
class UJ extends C0 {
  constructor(Q) {
    super();
    this.unit = Q;
  }
  get typeId() {
    return I.Interval;
  }
  toString() {
    return `Interval<${wQ[this.unit]}>`;
  }
}
EM = Symbol.toStringTag;
UJ[EM] = ((Q) => {
  return Q.unit = null, Q.ArrayType = Int32Array, Q[Symbol.toStringTag] = "Interval";
})(UJ.prototype);
class fX extends C0 {
  constructor(Q) {
    super();
    this.children = [Q];
  }
  get typeId() {
    return I.List;
  }
  toString() {
    return `List<${this.valueType}>`;
  }
  get valueType() {
    return this.children[0].type;
  }
  get valueField() {
    return this.children[0];
  }
  get ArrayType() {
    return this.valueType.ArrayType;
  }
}
FM = Symbol.toStringTag;
fX[FM] = ((Q) => {
  return Q.children = null, Q[Symbol.toStringTag] = "List";
})(fX.prototype);

class H6 extends C0 {
  constructor(Q) {
    super();
    this.children = Q;
  }
  get typeId() {
    return I.Struct;
  }
  toString() {
    return `Struct<{${this.children.map((Q) => `${Q.name}:${Q.type}`).join(", ")}}>`;
  }
}
UM = Symbol.toStringTag;
H6[UM] = ((Q) => {
  return Q.children = null, Q[Symbol.toStringTag] = "Struct";
})(H6.prototype);

class mX extends C0 {
  constructor(Q, J, Y) {
    super();
    this.mode = Q, this.children = Y, this.typeIds = J = Int32Array.from(J), this.typeIdToChildIndex = J.reduce((W, K, z) => (W[K] = z) && W || W, Object.create(null));
  }
  get typeId() {
    return I.Union;
  }
  toString() {
    return `${this[Symbol.toStringTag]}<${this.children.map((Q) => `${Q.type}`).join(" | ")}>`;
  }
}
PM = Symbol.toStringTag;
mX[PM] = ((Q) => {
  return Q.mode = null, Q.typeIds = null, Q.children = null, Q.typeIdToChildIndex = null, Q.ArrayType = Int8Array, Q[Symbol.toStringTag] = "Union";
})(mX.prototype);
class PJ extends C0 {
  constructor(Q) {
    super();
    this.byteWidth = Q;
  }
  get typeId() {
    return I.FixedSizeBinary;
  }
  toString() {
    return `FixedSizeBinary[${this.byteWidth}]`;
  }
}
AM = Symbol.toStringTag;
PJ[AM] = ((Q) => {
  return Q.byteWidth = null, Q.ArrayType = Uint8Array, Q[Symbol.toStringTag] = "FixedSizeBinary";
})(PJ.prototype);

class bX extends C0 {
  constructor(Q, J) {
    super();
    this.listSize = Q, this.children = [J];
  }
  get typeId() {
    return I.FixedSizeList;
  }
  get valueType() {
    return this.children[0].type;
  }
  get valueField() {
    return this.children[0];
  }
  get ArrayType() {
    return this.valueType.ArrayType;
  }
  toString() {
    return `FixedSizeList[${this.listSize}]<${this.valueType}>`;
  }
}
LM = Symbol.toStringTag;
bX[LM] = ((Q) => {
  return Q.children = null, Q.listSize = null, Q[Symbol.toStringTag] = "FixedSizeList";
})(bX.prototype);

class uX extends C0 {
  constructor(Q, J = !1) {
    super();
    this.children = [Q], this.keysSorted = J;
  }
  get typeId() {
    return I.Map;
  }
  get keyType() {
    return this.children[0].type.children[0].type;
  }
  get valueType() {
    return this.children[0].type.children[1].type;
  }
  get childType() {
    return this.children[0].type;
  }
  toString() {
    return `Map<{${this.children[0].type.children.map((Q) => `${Q.name}:${Q.type}`).join(", ")}}>`;
  }
}
OM = Symbol.toStringTag;
uX[OM] = ((Q) => {
  return Q.children = null, Q.keysSorted = null, Q[Symbol.toStringTag] = "Map_";
})(uX.prototype);
var Ov = ((Q) => () => ++Q)(-1);

class MZ extends C0 {
  constructor(Q, J, Y, W) {
    super();
    this.indices = J, this.dictionary = Q, this.isOrdered = W || !1, this.id = Y == null ? Ov() : typeof Y === "number" ? Y : Y.low;
  }
  get typeId() {
    return I.Dictionary;
  }
  get children() {
    return this.dictionary.children;
  }
  get valueType() {
    return this.dictionary;
  }
  get ArrayType() {
    return this.dictionary.ArrayType;
  }
  toString() {
    return `Dictionary<${this.indices}, ${this.dictionary}>`;
  }
}
wM = Symbol.toStringTag;
MZ[wM] = ((Q) => {
  return Q.id = null, Q.indices = null, Q.isOrdered = null, Q.dictionary = null, Q[Symbol.toStringTag] = "Dictionary";
})(MZ.prototype);
function JZ(Q) {
  let J = Q;
  switch (Q.typeId) {
    case I.Decimal:
      return Q.bitWidth / 32;
    case I.Timestamp:
      return 2;
    case I.Date:
      return 1 + J.unit;
    case I.Interval:
      return 1 + J.unit;
    case I.FixedSizeList:
      return J.listSize;
    case I.FixedSizeBinary:
      return J.byteWidth;
    default:
      return 1;
  }
}

// node_modules/apache-arrow/visitor.mjs
class y0 {
  visitMany(Q, ...J) {
    return Q.map((Y, W) => this.visit(Y, ...J.map((K) => K[W])));
  }
  visit(...Q) {
    return this.getVisitFn(Q[0], !1).apply(this, Q);
  }
  getVisitFn(Q, J = !0) {
    return wv(this, Q, J);
  }
  getVisitFnByTypeId(Q, J = !0) {
    return Zq(this, Q, J);
  }
  visitNull(Q, ...J) {
    return null;
  }
  visitBool(Q, ...J) {
    return null;
  }
  visitInt(Q, ...J) {
    return null;
  }
  visitFloat(Q, ...J) {
    return null;
  }
  visitUtf8(Q, ...J) {
    return null;
  }
  visitBinary(Q, ...J) {
    return null;
  }
  visitFixedSizeBinary(Q, ...J) {
    return null;
  }
  visitDate(Q, ...J) {
    return null;
  }
  visitTimestamp(Q, ...J) {
    return null;
  }
  visitTime(Q, ...J) {
    return null;
  }
  visitDecimal(Q, ...J) {
    return null;
  }
  visitList(Q, ...J) {
    return null;
  }
  visitStruct(Q, ...J) {
    return null;
  }
  visitUnion(Q, ...J) {
    return null;
  }
  visitDictionary(Q, ...J) {
    return null;
  }
  visitInterval(Q, ...J) {
    return null;
  }
  visitFixedSizeList(Q, ...J) {
    return null;
  }
  visitMap(Q, ...J) {
    return null;
  }
}
function wv(Q, J, Y = !0) {
  if (typeof J === "number")
    return Zq(Q, J, Y);
  if (typeof J === "string" && J in I)
    return Zq(Q, I[J], Y);
  if (J && J instanceof C0)
    return Zq(Q, MM(J), Y);
  if ((J === null || J === void 0 ? void 0 : J.type) && J.type instanceof C0)
    return Zq(Q, MM(J.type), Y);
  return Zq(Q, I.NONE, Y);
}
function Zq(Q, J, Y = !0) {
  let W = null;
  switch (J) {
    case I.Null:
      W = Q.visitNull;
      break;
    case I.Bool:
      W = Q.visitBool;
      break;
    case I.Int:
      W = Q.visitInt;
      break;
    case I.Int8:
      W = Q.visitInt8 || Q.visitInt;
      break;
    case I.Int16:
      W = Q.visitInt16 || Q.visitInt;
      break;
    case I.Int32:
      W = Q.visitInt32 || Q.visitInt;
      break;
    case I.Int64:
      W = Q.visitInt64 || Q.visitInt;
      break;
    case I.Uint8:
      W = Q.visitUint8 || Q.visitInt;
      break;
    case I.Uint16:
      W = Q.visitUint16 || Q.visitInt;
      break;
    case I.Uint32:
      W = Q.visitUint32 || Q.visitInt;
      break;
    case I.Uint64:
      W = Q.visitUint64 || Q.visitInt;
      break;
    case I.Float:
      W = Q.visitFloat;
      break;
    case I.Float16:
      W = Q.visitFloat16 || Q.visitFloat;
      break;
    case I.Float32:
      W = Q.visitFloat32 || Q.visitFloat;
      break;
    case I.Float64:
      W = Q.visitFloat64 || Q.visitFloat;
      break;
    case I.Utf8:
      W = Q.visitUtf8;
      break;
    case I.Binary:
      W = Q.visitBinary;
      break;
    case I.FixedSizeBinary:
      W = Q.visitFixedSizeBinary;
      break;
    case I.Date:
      W = Q.visitDate;
      break;
    case I.DateDay:
      W = Q.visitDateDay || Q.visitDate;
      break;
    case I.DateMillisecond:
      W = Q.visitDateMillisecond || Q.visitDate;
      break;
    case I.Timestamp:
      W = Q.visitTimestamp;
      break;
    case I.TimestampSecond:
      W = Q.visitTimestampSecond || Q.visitTimestamp;
      break;
    case I.TimestampMillisecond:
      W = Q.visitTimestampMillisecond || Q.visitTimestamp;
      break;
    case I.TimestampMicrosecond:
      W = Q.visitTimestampMicrosecond || Q.visitTimestamp;
      break;
    case I.TimestampNanosecond:
      W = Q.visitTimestampNanosecond || Q.visitTimestamp;
      break;
    case I.Time:
      W = Q.visitTime;
      break;
    case I.TimeSecond:
      W = Q.visitTimeSecond || Q.visitTime;
      break;
    case I.TimeMillisecond:
      W = Q.visitTimeMillisecond || Q.visitTime;
      break;
    case I.TimeMicrosecond:
      W = Q.visitTimeMicrosecond || Q.visitTime;
      break;
    case I.TimeNanosecond:
      W = Q.visitTimeNanosecond || Q.visitTime;
      break;
    case I.Decimal:
      W = Q.visitDecimal;
      break;
    case I.List:
      W = Q.visitList;
      break;
    case I.Struct:
      W = Q.visitStruct;
      break;
    case I.Union:
      W = Q.visitUnion;
      break;
    case I.DenseUnion:
      W = Q.visitDenseUnion || Q.visitUnion;
      break;
    case I.SparseUnion:
      W = Q.visitSparseUnion || Q.visitUnion;
      break;
    case I.Dictionary:
      W = Q.visitDictionary;
      break;
    case I.Interval:
      W = Q.visitInterval;
      break;
    case I.IntervalDayTime:
      W = Q.visitIntervalDayTime || Q.visitInterval;
      break;
    case I.IntervalYearMonth:
      W = Q.visitIntervalYearMonth || Q.visitInterval;
      break;
    case I.FixedSizeList:
      W = Q.visitFixedSizeList;
      break;
    case I.Map:
      W = Q.visitMap;
      break;
  }
  if (typeof W === "function")
    return W;
  if (!Y)
    return () => null;
  throw new Error(`Unrecognized type '${I[J]}'`);
}
function MM(Q) {
  switch (Q.typeId) {
    case I.Null:
      return I.Null;
    case I.Int: {
      let { bitWidth: J, isSigned: Y } = Q;
      switch (J) {
        case 8:
          return Y ? I.Int8 : I.Uint8;
        case 16:
          return Y ? I.Int16 : I.Uint16;
        case 32:
          return Y ? I.Int32 : I.Uint32;
        case 64:
          return Y ? I.Int64 : I.Uint64;
      }
      return I.Int;
    }
    case I.Float:
      switch (Q.precision) {
        case K6.HALF:
          return I.Float16;
        case K6.SINGLE:
          return I.Float32;
        case K6.DOUBLE:
          return I.Float64;
      }
      return I.Float;
    case I.Binary:
      return I.Binary;
    case I.Utf8:
      return I.Utf8;
    case I.Bool:
      return I.Bool;
    case I.Decimal:
      return I.Decimal;
    case I.Time:
      switch (Q.unit) {
        case F1.SECOND:
          return I.TimeSecond;
        case F1.MILLISECOND:
          return I.TimeMillisecond;
        case F1.MICROSECOND:
          return I.TimeMicrosecond;
        case F1.NANOSECOND:
          return I.TimeNanosecond;
      }
      return I.Time;
    case I.Timestamp:
      switch (Q.unit) {
        case F1.SECOND:
          return I.TimestampSecond;
        case F1.MILLISECOND:
          return I.TimestampMillisecond;
        case F1.MICROSECOND:
          return I.TimestampMicrosecond;
        case F1.NANOSECOND:
          return I.TimestampNanosecond;
      }
      return I.Timestamp;
    case I.Date:
      switch (Q.unit) {
        case f8.DAY:
          return I.DateDay;
        case f8.MILLISECOND:
          return I.DateMillisecond;
      }
      return I.Date;
    case I.Interval:
      switch (Q.unit) {
        case wQ.DAY_TIME:
          return I.IntervalDayTime;
        case wQ.YEAR_MONTH:
          return I.IntervalYearMonth;
      }
      return I.Interval;
    case I.Map:
      return I.Map;
    case I.List:
      return I.List;
    case I.Struct:
      return I.Struct;
    case I.Union:
      switch (Q.mode) {
        case k6.Dense:
          return I.DenseUnion;
        case k6.Sparse:
          return I.SparseUnion;
      }
      return I.Union;
    case I.FixedSizeBinary:
      return I.FixedSizeBinary;
    case I.FixedSizeList:
      return I.FixedSizeList;
    case I.Dictionary:
      return I.Dictionary;
  }
  throw new Error(`Unrecognized type '${I[Q.typeId]}'`);
}
y0.prototype.visitInt8 = null;
y0.prototype.visitInt16 = null;
y0.prototype.visitInt32 = null;
y0.prototype.visitInt64 = null;
y0.prototype.visitUint8 = null;
y0.prototype.visitUint16 = null;
y0.prototype.visitUint32 = null;
y0.prototype.visitUint64 = null;
y0.prototype.visitFloat16 = null;
y0.prototype.visitFloat32 = null;
y0.prototype.visitFloat64 = null;
y0.prototype.visitDateDay = null;
y0.prototype.visitDateMillisecond = null;
y0.prototype.visitTimestampSecond = null;
y0.prototype.visitTimestampMillisecond = null;
y0.prototype.visitTimestampMicrosecond = null;
y0.prototype.visitTimestampNanosecond = null;
y0.prototype.visitTimeSecond = null;
y0.prototype.visitTimeMillisecond = null;
y0.prototype.visitTimeMicrosecond = null;
y0.prototype.visitTimeNanosecond = null;
y0.prototype.visitDenseUnion = null;
y0.prototype.visitSparseUnion = null;
y0.prototype.visitIntervalDayTime = null;
y0.prototype.visitIntervalYearMonth = null;

// node_modules/apache-arrow/util/math.mjs
var bN = {};
sY(bN, {
  uint16ToFloat64: () => f5,
  float64ToUint16: () => R3
});
var DM = new Float64Array(1), Xq = new Uint32Array(DM.buffer);
function f5(Q) {
  let J = (Q & 31744) >> 10, Y = (Q & 1023) / 1024, W = Math.pow(-1, (Q & 32768) >> 15);
  switch (J) {
    case 31:
      return W * (Y ? Number.NaN : 1 / 0);
    case 0:
      return W * (Y ? 0.00006103515625 * Y : 0);
  }
  return W * Math.pow(2, J - 15) * (1 + Y);
}
function R3(Q) {
  if (Q !== Q)
    return 32256;
  DM[0] = Q;
  let J = (Xq[1] & 2147483648) >> 16 & 65535, Y = Xq[1] & 2146435072, W = 0;
  if (Y >= 1089470464)
    if (Xq[0] > 0)
      Y = 31744;
    else
      Y = (Y & 2080374784) >> 16, W = (Xq[1] & 1048575) >> 10;
  else if (Y <= 1056964608)
    W = 1048576 + (Xq[1] & 1048575), W = 1048576 + (W << (Y >> 20) - 998) >> 21, Y = 0;
  else
    Y = Y - 1056964608 >> 10, W = (Xq[1] & 1048575) + 512 >> 10;
  return J | Y | W & 65535;
}

// node_modules/apache-arrow/visitor/set.mjs
class t0 extends y0 {
}
function $1(Q) {
  return (J, Y, W) => {
    if (J.setValid(Y, W != null))
      return Q(J, Y, W);
  };
}
var Mv = (Q, J, Y) => {
  Q[J] = Math.trunc(Y / 86400000);
}, uN = (Q, J, Y) => {
  Q[J] = Math.trunc(Y % 4294967296), Q[J + 1] = Math.trunc(Y / 4294967296);
}, Dv = (Q, J, Y) => {
  Q[J] = Math.trunc(Y * 1000 % 4294967296), Q[J + 1] = Math.trunc(Y * 1000 / 4294967296);
}, kv = (Q, J, Y) => {
  Q[J] = Math.trunc(Y * 1e6 % 4294967296), Q[J + 1] = Math.trunc(Y * 1e6 / 4294967296);
}, kM = (Q, J, Y, W) => {
  if (Y + 1 < J.length) {
    let { [Y]: K, [Y + 1]: z } = J;
    Q.set(W.subarray(0, z - K), K);
  }
}, Rv = ({ offset: Q, values: J }, Y, W) => {
  let K = Q + Y;
  W ? J[K >> 3] |= 1 << K % 8 : J[K >> 3] &= ~(1 << K % 8);
}, O4 = ({ values: Q }, J, Y) => {
  Q[J] = Y;
}, cN = ({ values: Q }, J, Y) => {
  Q[J] = Y;
}, RM = ({ values: Q }, J, Y) => {
  Q[J] = R3(Y);
}, jv = (Q, J, Y) => {
  switch (Q.type.precision) {
    case K6.HALF:
      return RM(Q, J, Y);
    case K6.SINGLE:
    case K6.DOUBLE:
      return cN(Q, J, Y);
  }
}, m5 = ({ values: Q }, J, Y) => {
  Mv(Q, J, Y.valueOf());
}, b5 = ({ values: Q }, J, Y) => {
  uN(Q, J * 2, Y.valueOf());
}, pN = ({ stride: Q, values: J }, Y, W) => {
  J.set(W.subarray(0, Q), Q * Y);
}, Bv = ({ values: Q, valueOffsets: J }, Y, W) => kM(Q, J, Y, W), Cv = ({ values: Q, valueOffsets: J }, Y, W) => {
  kM(Q, J, Y, WJ(W));
}, dN = (Q, J, Y) => {
  Q.type.unit === f8.DAY ? m5(Q, J, Y) : b5(Q, J, Y);
}, u5 = ({ values: Q }, J, Y) => uN(Q, J * 2, Y / 1000), c5 = ({ values: Q }, J, Y) => uN(Q, J * 2, Y), p5 = ({ values: Q }, J, Y) => Dv(Q, J * 2, Y), d5 = ({ values: Q }, J, Y) => kv(Q, J * 2, Y), lN = (Q, J, Y) => {
  switch (Q.type.unit) {
    case F1.SECOND:
      return u5(Q, J, Y);
    case F1.MILLISECOND:
      return c5(Q, J, Y);
    case F1.MICROSECOND:
      return p5(Q, J, Y);
    case F1.NANOSECOND:
      return d5(Q, J, Y);
  }
}, l5 = ({ values: Q }, J, Y) => {
  Q[J] = Y;
}, n5 = ({ values: Q }, J, Y) => {
  Q[J] = Y;
}, s5 = ({ values: Q }, J, Y) => {
  Q[J] = Y;
}, o5 = ({ values: Q }, J, Y) => {
  Q[J] = Y;
}, nN = (Q, J, Y) => {
  switch (Q.type.unit) {
    case F1.SECOND:
      return l5(Q, J, Y);
    case F1.MILLISECOND:
      return n5(Q, J, Y);
    case F1.MICROSECOND:
      return s5(Q, J, Y);
    case F1.NANOSECOND:
      return o5(Q, J, Y);
  }
}, sN = ({ values: Q, stride: J }, Y, W) => {
  Q.set(W.subarray(0, J), J * Y);
}, Vv = (Q, J, Y) => {
  let W = Q.children[0], K = Q.valueOffsets, z = m8.getVisitFn(W);
  if (Array.isArray(Y))
    for (let N = -1, F = K[J], L = K[J + 1];F < L; )
      z(W, F++, Y[++N]);
  else
    for (let N = -1, F = K[J], L = K[J + 1];F < L; )
      z(W, F++, Y.get(++N));
}, Sv = (Q, J, Y) => {
  let W = Q.children[0], { valueOffsets: K } = Q, z = m8.getVisitFn(W), { [J]: N, [J + 1]: F } = K, L = Y instanceof Map ? Y.entries() : Object.entries(Y);
  for (let w of L)
    if (z(W, N, w), ++N >= F)
      break;
}, Iv = (Q, J) => (Y, W, K, z) => W && Y(W, Q, J[z]), _v = (Q, J) => (Y, W, K, z) => W && Y(W, Q, J.get(z)), Tv = (Q, J) => (Y, W, K, z) => W && Y(W, Q, J.get(K.name)), gv = (Q, J) => (Y, W, K, z) => W && Y(W, Q, J[K.name]), xv = (Q, J, Y) => {
  let W = Q.type.children.map((z) => m8.getVisitFn(z.type)), K = Y instanceof Map ? Tv(J, Y) : Y instanceof Z1 ? _v(J, Y) : Array.isArray(Y) ? Iv(J, Y) : gv(J, Y);
  Q.type.children.forEach((z, N) => K(W[N], Q.children[N], z, N));
}, vv = (Q, J, Y) => {
  Q.type.mode === k6.Dense ? jM(Q, J, Y) : BM(Q, J, Y);
}, jM = (Q, J, Y) => {
  let W = Q.type.typeIdToChildIndex[Q.typeIds[J]], K = Q.children[W];
  m8.visit(K, Q.valueOffsets[J], Y);
}, BM = (Q, J, Y) => {
  let W = Q.type.typeIdToChildIndex[Q.typeIds[J]], K = Q.children[W];
  m8.visit(K, J, Y);
}, hv = (Q, J, Y) => {
  var W;
  (W = Q.dictionary) === null || W === void 0 || W.set(Q.values[J], Y);
}, oN = (Q, J, Y) => {
  Q.type.unit === wQ.DAY_TIME ? a5(Q, J, Y) : r5(Q, J, Y);
}, a5 = ({ values: Q }, J, Y) => {
  Q.set(Y.subarray(0, 2), 2 * J);
}, r5 = ({ values: Q }, J, Y) => {
  Q[J] = Y[0] * 12 + Y[1] % 12;
}, yv = (Q, J, Y) => {
  let { stride: W } = Q, K = Q.children[0], z = m8.getVisitFn(K);
  if (Array.isArray(Y))
    for (let N = -1, F = J * W;++N < W; )
      z(K, F + N, Y[N]);
  else
    for (let N = -1, F = J * W;++N < W; )
      z(K, F + N, Y.get(N));
};
t0.prototype.visitBool = $1(Rv);
t0.prototype.visitInt = $1(O4);
t0.prototype.visitInt8 = $1(O4);
t0.prototype.visitInt16 = $1(O4);
t0.prototype.visitInt32 = $1(O4);
t0.prototype.visitInt64 = $1(O4);
t0.prototype.visitUint8 = $1(O4);
t0.prototype.visitUint16 = $1(O4);
t0.prototype.visitUint32 = $1(O4);
t0.prototype.visitUint64 = $1(O4);
t0.prototype.visitFloat = $1(jv);
t0.prototype.visitFloat16 = $1(RM);
t0.prototype.visitFloat32 = $1(cN);
t0.prototype.visitFloat64 = $1(cN);
t0.prototype.visitUtf8 = $1(Cv);
t0.prototype.visitBinary = $1(Bv);
t0.prototype.visitFixedSizeBinary = $1(pN);
t0.prototype.visitDate = $1(dN);
t0.prototype.visitDateDay = $1(m5);
t0.prototype.visitDateMillisecond = $1(b5);
t0.prototype.visitTimestamp = $1(lN);
t0.prototype.visitTimestampSecond = $1(u5);
t0.prototype.visitTimestampMillisecond = $1(c5);
t0.prototype.visitTimestampMicrosecond = $1(p5);
t0.prototype.visitTimestampNanosecond = $1(d5);
t0.prototype.visitTime = $1(nN);
t0.prototype.visitTimeSecond = $1(l5);
t0.prototype.visitTimeMillisecond = $1(n5);
t0.prototype.visitTimeMicrosecond = $1(s5);
t0.prototype.visitTimeNanosecond = $1(o5);
t0.prototype.visitDecimal = $1(sN);
t0.prototype.visitList = $1(Vv);
t0.prototype.visitStruct = $1(xv);
t0.prototype.visitUnion = $1(vv);
t0.prototype.visitDenseUnion = $1(jM);
t0.prototype.visitSparseUnion = $1(BM);
t0.prototype.visitDictionary = $1(hv);
t0.prototype.visitInterval = $1(oN);
t0.prototype.visitIntervalDayTime = $1(a5);
t0.prototype.visitIntervalYearMonth = $1(r5);
t0.prototype.visitFixedSizeList = $1(yv);
t0.prototype.visitMap = $1(Sv);
var m8 = new t0;

// node_modules/apache-arrow/row/struct.mjs
var qX = Symbol.for("parent"), Jq = Symbol.for("rowIndex");

class R$ {
  constructor(Q, J) {
    return this[qX] = Q, this[Jq] = J, new Proxy(this, new VM);
  }
  toArray() {
    return Object.values(this.toJSON());
  }
  toJSON() {
    let Q = this[Jq], J = this[qX], Y = J.type.children, W = {};
    for (let K = -1, z = Y.length;++K < z; )
      W[Y[K].name] = c6.visit(J.children[K], Q);
    return W;
  }
  toString() {
    return `{${[...this].map(([Q, J]) => `${$X(Q)}: ${$X(J)}`).join(", ")}}`;
  }
  [Symbol.for("nodejs.util.inspect.custom")]() {
    return this.toString();
  }
  [Symbol.iterator]() {
    return new CM(this[qX], this[Jq]);
  }
}

class CM {
  constructor(Q, J) {
    this.childIndex = 0, this.children = Q.children, this.rowIndex = J, this.childFields = Q.type.children, this.numChildren = this.childFields.length;
  }
  [Symbol.iterator]() {
    return this;
  }
  next() {
    let Q = this.childIndex;
    if (Q < this.numChildren)
      return this.childIndex = Q + 1, {
        done: !1,
        value: [
          this.childFields[Q].name,
          c6.visit(this.children[Q], this.rowIndex)
        ]
      };
    return { done: !0, value: null };
  }
}
Object.defineProperties(R$.prototype, {
  [Symbol.toStringTag]: { enumerable: !1, configurable: !1, value: "Row" },
  [qX]: { writable: !0, enumerable: !1, configurable: !1, value: null },
  [Jq]: { writable: !0, enumerable: !1, configurable: !1, value: -1 }
});

class VM {
  isExtensible() {
    return !1;
  }
  deleteProperty() {
    return !1;
  }
  preventExtensions() {
    return !0;
  }
  ownKeys(Q) {
    return Q[qX].type.children.map((J) => J.name);
  }
  has(Q, J) {
    return Q[qX].type.children.findIndex((Y) => Y.name === J) !== -1;
  }
  getOwnPropertyDescriptor(Q, J) {
    if (Q[qX].type.children.findIndex((Y) => Y.name === J) !== -1)
      return { writable: !0, enumerable: !0, configurable: !0 };
    return;
  }
  get(Q, J) {
    if (Reflect.has(Q, J))
      return Q[J];
    let Y = Q[qX].type.children.findIndex((W) => W.name === J);
    if (Y !== -1) {
      let W = c6.visit(Q[qX].children[Y], Q[Jq]);
      return Reflect.set(Q, J, W), W;
    }
  }
  set(Q, J, Y) {
    let W = Q[qX].type.children.findIndex((K) => K.name === J);
    if (W !== -1)
      return m8.visit(Q[qX].children[W], Q[Jq], Y), Reflect.set(Q, J, Y);
    else if (Reflect.has(Q, J) || typeof J === "symbol")
      return Reflect.set(Q, J, Y);
    return !1;
  }
}

// node_modules/apache-arrow/visitor/get.mjs
class s0 extends y0 {
}
function X1(Q) {
  return (J, Y) => J.getValid(Y) ? Q(J, Y) : null;
}
var fv = (Q, J) => 86400000 * Q[J], aN = (Q, J) => 4294967296 * Q[J + 1] + (Q[J] >>> 0), mv = (Q, J) => 4294967296 * (Q[J + 1] / 1000) + (Q[J] >>> 0) / 1000, bv = (Q, J) => 4294967296 * (Q[J + 1] / 1e6) + (Q[J] >>> 0) / 1e6, SM = (Q) => new Date(Q), uv = (Q, J) => SM(fv(Q, J)), cv = (Q, J) => SM(aN(Q, J)), pv = (Q, J) => null, IM = (Q, J, Y) => {
  if (Y + 1 >= J.length)
    return null;
  let W = J[Y], K = J[Y + 1];
  return Q.subarray(W, K);
}, dv = ({ offset: Q, values: J }, Y) => {
  let W = Q + Y;
  return (J[W >> 3] & 1 << W % 8) !== 0;
}, _M = ({ values: Q }, J) => uv(Q, J), TM = ({ values: Q }, J) => cv(Q, J * 2), AJ = ({ stride: Q, values: J }, Y) => J[Q * Y], lv = ({ stride: Q, values: J }, Y) => f5(J[Q * Y]), gM = ({ values: Q }, J) => Q[J], nv = ({ stride: Q, values: J }, Y) => J.subarray(Q * Y, Q * (Y + 1)), sv = ({ values: Q, valueOffsets: J }, Y) => IM(Q, J, Y), ov = ({ values: Q, valueOffsets: J }, Y) => {
  let W = IM(Q, J, Y);
  return W !== null ? O3(W) : null;
}, av = ({ values: Q }, J) => Q[J], rv = ({ type: Q, values: J }, Y) => Q.precision !== K6.HALF ? J[Y] : f5(J[Y]), iv = (Q, J) => Q.type.unit === f8.DAY ? _M(Q, J) : TM(Q, J), xM = ({ values: Q }, J) => 1000 * aN(Q, J * 2), vM = ({ values: Q }, J) => aN(Q, J * 2), hM = ({ values: Q }, J) => mv(Q, J * 2), yM = ({ values: Q }, J) => bv(Q, J * 2), tv = (Q, J) => {
  switch (Q.type.unit) {
    case F1.SECOND:
      return xM(Q, J);
    case F1.MILLISECOND:
      return vM(Q, J);
    case F1.MICROSECOND:
      return hM(Q, J);
    case F1.NANOSECOND:
      return yM(Q, J);
  }
}, fM = ({ values: Q }, J) => Q[J], mM = ({ values: Q }, J) => Q[J], bM = ({ values: Q }, J) => Q[J], uM = ({ values: Q }, J) => Q[J], ev = (Q, J) => {
  switch (Q.type.unit) {
    case F1.SECOND:
      return fM(Q, J);
    case F1.MILLISECOND:
      return mM(Q, J);
    case F1.MICROSECOND:
      return bM(Q, J);
    case F1.NANOSECOND:
      return uM(Q, J);
  }
}, Qh = ({ values: Q, stride: J }, Y) => k3.decimal(Q.subarray(J * Y, J * (Y + 1))), Zh = (Q, J) => {
  let { valueOffsets: Y, stride: W, children: K } = Q, { [J * W]: z, [J * W + 1]: N } = Y, L = K[0].slice(z, N - z);
  return new Z1([L]);
}, Xh = (Q, J) => {
  let { valueOffsets: Y, children: W } = Q, { [J]: K, [J + 1]: z } = Y, N = W[0];
  return new w4(N.slice(K, z - K));
}, Jh = (Q, J) => {
  return new R$(Q, J);
}, $h = (Q, J) => {
  return Q.type.mode === k6.Dense ? cM(Q, J) : pM(Q, J);
}, cM = (Q, J) => {
  let Y = Q.type.typeIdToChildIndex[Q.typeIds[J]], W = Q.children[Y];
  return c6.visit(W, Q.valueOffsets[J]);
}, pM = (Q, J) => {
  let Y = Q.type.typeIdToChildIndex[Q.typeIds[J]], W = Q.children[Y];
  return c6.visit(W, J);
}, Yh = (Q, J) => {
  var Y;
  return (Y = Q.dictionary) === null || Y === void 0 ? void 0 : Y.get(Q.values[J]);
}, qh = (Q, J) => Q.type.unit === wQ.DAY_TIME ? dM(Q, J) : lM(Q, J), dM = ({ values: Q }, J) => Q.subarray(2 * J, 2 * (J + 1)), lM = ({ values: Q }, J) => {
  let Y = Q[J], W = new Int32Array(2);
  return W[0] = Math.trunc(Y / 12), W[1] = Math.trunc(Y % 12), W;
}, Wh = (Q, J) => {
  let { stride: Y, children: W } = Q, z = W[0].slice(J * Y, Y);
  return new Z1([z]);
};
s0.prototype.visitNull = X1(pv);
s0.prototype.visitBool = X1(dv);
s0.prototype.visitInt = X1(av);
s0.prototype.visitInt8 = X1(AJ);
s0.prototype.visitInt16 = X1(AJ);
s0.prototype.visitInt32 = X1(AJ);
s0.prototype.visitInt64 = X1(gM);
s0.prototype.visitUint8 = X1(AJ);
s0.prototype.visitUint16 = X1(AJ);
s0.prototype.visitUint32 = X1(AJ);
s0.prototype.visitUint64 = X1(gM);
s0.prototype.visitFloat = X1(rv);
s0.prototype.visitFloat16 = X1(lv);
s0.prototype.visitFloat32 = X1(AJ);
s0.prototype.visitFloat64 = X1(AJ);
s0.prototype.visitUtf8 = X1(ov);
s0.prototype.visitBinary = X1(sv);
s0.prototype.visitFixedSizeBinary = X1(nv);
s0.prototype.visitDate = X1(iv);
s0.prototype.visitDateDay = X1(_M);
s0.prototype.visitDateMillisecond = X1(TM);
s0.prototype.visitTimestamp = X1(tv);
s0.prototype.visitTimestampSecond = X1(xM);
s0.prototype.visitTimestampMillisecond = X1(vM);
s0.prototype.visitTimestampMicrosecond = X1(hM);
s0.prototype.visitTimestampNanosecond = X1(yM);
s0.prototype.visitTime = X1(ev);
s0.prototype.visitTimeSecond = X1(fM);
s0.prototype.visitTimeMillisecond = X1(mM);
s0.prototype.visitTimeMicrosecond = X1(bM);
s0.prototype.visitTimeNanosecond = X1(uM);
s0.prototype.visitDecimal = X1(Qh);
s0.prototype.visitList = X1(Zh);
s0.prototype.visitStruct = X1(Jh);
s0.prototype.visitUnion = X1($h);
s0.prototype.visitDenseUnion = X1(cM);
s0.prototype.visitSparseUnion = X1(pM);
s0.prototype.visitDictionary = X1(Yh);
s0.prototype.visitInterval = X1(qh);
s0.prototype.visitIntervalDayTime = X1(dM);
s0.prototype.visitIntervalYearMonth = X1(lM);
s0.prototype.visitFixedSizeList = X1(Wh);
s0.prototype.visitMap = X1(Xh);
var c6 = new s0;

// node_modules/apache-arrow/row/map.mjs
var DZ = Symbol.for("keys"), $q = Symbol.for("vals");

class w4 {
  constructor(Q) {
    return this[DZ] = new Z1([Q.children[0]]).memoize(), this[$q] = Q.children[1], new Proxy(this, new sM);
  }
  [Symbol.iterator]() {
    return new nM(this[DZ], this[$q]);
  }
  get size() {
    return this[DZ].length;
  }
  toArray() {
    return Object.values(this.toJSON());
  }
  toJSON() {
    let Q = this[DZ], J = this[$q], Y = {};
    for (let W = -1, K = Q.length;++W < K; )
      Y[Q.get(W)] = c6.visit(J, W);
    return Y;
  }
  toString() {
    return `{${[...this].map(([Q, J]) => `${$X(Q)}: ${$X(J)}`).join(", ")}}`;
  }
  [Symbol.for("nodejs.util.inspect.custom")]() {
    return this.toString();
  }
}

class nM {
  constructor(Q, J) {
    this.keys = Q, this.vals = J, this.keyIndex = 0, this.numKeys = Q.length;
  }
  [Symbol.iterator]() {
    return this;
  }
  next() {
    let Q = this.keyIndex;
    if (Q === this.numKeys)
      return { done: !0, value: null };
    return this.keyIndex++, {
      done: !1,
      value: [
        this.keys.get(Q),
        c6.visit(this.vals, Q)
      ]
    };
  }
}

class sM {
  isExtensible() {
    return !1;
  }
  deleteProperty() {
    return !1;
  }
  preventExtensions() {
    return !0;
  }
  ownKeys(Q) {
    return Q[DZ].toArray().map(String);
  }
  has(Q, J) {
    return Q[DZ].includes(J);
  }
  getOwnPropertyDescriptor(Q, J) {
    if (Q[DZ].indexOf(J) !== -1)
      return { writable: !0, enumerable: !0, configurable: !0 };
    return;
  }
  get(Q, J) {
    if (Reflect.has(Q, J))
      return Q[J];
    let Y = Q[DZ].indexOf(J);
    if (Y !== -1) {
      let W = c6.visit(Reflect.get(Q, $q), Y);
      return Reflect.set(Q, J, W), W;
    }
  }
  set(Q, J, Y) {
    let W = Q[DZ].indexOf(J);
    if (W !== -1)
      return m8.visit(Reflect.get(Q, $q), W, Y), Reflect.set(Q, J, Y);
    else if (Reflect.has(Q, J))
      return Reflect.set(Q, J, Y);
    return !1;
  }
}
Object.defineProperties(w4.prototype, {
  [Symbol.toStringTag]: { enumerable: !1, configurable: !1, value: "Row" },
  [DZ]: { writable: !0, enumerable: !1, configurable: !1, value: null },
  [$q]: { writable: !0, enumerable: !1, configurable: !1, value: null }
});

// node_modules/apache-arrow/util/vector.mjs
function Kh(Q, J, Y) {
  let W = Q.length, K = J > -1 ? J : W + J % W;
  return Y ? Y(Q, K) : K;
}
var oM;
function j3(Q, J, Y, W) {
  let { length: K = 0 } = Q, z = typeof J !== "number" ? 0 : J, N = typeof Y !== "number" ? K : Y;
  return z < 0 && (z = (z % K + K) % K), N < 0 && (N = (N % K + K) % K), N < z && (oM = z, z = N, N = oM), N > K && (N = K), W ? W(Q, z, N) : [z, N];
}
var aM = (Q) => Q !== Q;
function LJ(Q) {
  if (typeof Q !== "object" || Q === null) {
    if (aM(Q))
      return aM;
    return (Y) => Y === Q;
  }
  if (Q instanceof Date) {
    let Y = Q.valueOf();
    return (W) => W instanceof Date ? W.valueOf() === Y : !1;
  }
  if (ArrayBuffer.isView(Q))
    return (Y) => Y ? jN(Q, Y) : !1;
  if (Q instanceof Map)
    return Gh(Q);
  if (Array.isArray(Q))
    return Hh(Q);
  if (Q instanceof Z1)
    return zh(Q);
  return Nh(Q, !0);
}
function Hh(Q) {
  let J = [];
  for (let Y = -1, W = Q.length;++Y < W; )
    J[Y] = LJ(Q[Y]);
  return i5(J);
}
function Gh(Q) {
  let J = -1, Y = [];
  for (let W of Q.values())
    Y[++J] = LJ(W);
  return i5(Y);
}
function zh(Q) {
  let J = [];
  for (let Y = -1, W = Q.length;++Y < W; )
    J[Y] = LJ(Q.get(Y));
  return i5(J);
}
function Nh(Q, J = !1) {
  let Y = Object.keys(Q);
  if (!J && Y.length === 0)
    return () => !1;
  let W = [];
  for (let K = -1, z = Y.length;++K < z; )
    W[K] = LJ(Q[Y[K]]);
  return i5(W, Y);
}
function i5(Q, J) {
  return (Y) => {
    if (!Y || typeof Y !== "object")
      return !1;
    switch (Y.constructor) {
      case Array:
        return Eh(Q, Y);
      case Map:
        return rM(Q, Y, Y.keys());
      case w4:
      case R$:
      case Object:
      case void 0:
        return rM(Q, Y, J || Object.keys(Y));
    }
    return Y instanceof Z1 ? Fh(Q, Y) : !1;
  };
}
function Eh(Q, J) {
  let Y = Q.length;
  if (J.length !== Y)
    return !1;
  for (let W = -1;++W < Y; )
    if (!Q[W](J[W]))
      return !1;
  return !0;
}
function Fh(Q, J) {
  let Y = Q.length;
  if (J.length !== Y)
    return !1;
  for (let W = -1;++W < Y; )
    if (!Q[W](J.get(W)))
      return !1;
  return !0;
}
function rM(Q, J, Y) {
  let W = Y[Symbol.iterator](), K = J instanceof Map ? J.keys() : Object.keys(J)[Symbol.iterator](), z = J instanceof Map ? J.values() : Object.values(J)[Symbol.iterator](), N = 0, F = Q.length, L = z.next(), w = W.next(), D = K.next();
  for (;N < F && !w.done && !D.done && !L.done; ++N, w = W.next(), D = K.next(), L = z.next())
    if (w.value !== D.value || !Q[N](L.value))
      break;
  if (N === F && w.done && D.done && L.done)
    return !0;
  return W.return && W.return(), K.return && K.return(), z.return && z.return(), !1;
}

// node_modules/apache-arrow/util/bit.mjs
var iN = {};
sY(iN, {
  truncateBitmap: () => Yq,
  setBool: () => Uh,
  popcnt_uint32: () => t5,
  popcnt_bit_range: () => B3,
  popcnt_array: () => tM,
  packBools: () => j$,
  getBool: () => e5,
  getBit: () => iM,
  BitIterator: () => qq
});
function e5(Q, J, Y, W) {
  return (Y & 1 << W) !== 0;
}
function iM(Q, J, Y, W) {
  return (Y & 1 << W) >> W;
}
function Uh(Q, J, Y) {
  return Y ? !!(Q[J >> 3] |= 1 << J % 8) || !0 : !(Q[J >> 3] &= ~(1 << J % 8)) && !1;
}
function Yq(Q, J, Y) {
  let W = Y.byteLength + 7 & -8;
  if (Q > 0 || Y.byteLength < W) {
    let K = new Uint8Array(W);
    return K.set(Q % 8 === 0 ? Y.subarray(Q >> 3) : j$(new qq(Y, Q, J, null, e5)).subarray(0, W)), K;
  }
  return Y;
}
function j$(Q) {
  let J = [], Y = 0, W = 0, K = 0;
  for (let N of Q)
    if (N && (K |= 1 << W), ++W === 8)
      J[Y++] = K, K = W = 0;
  if (Y === 0 || W > 0)
    J[Y++] = K;
  let z = new Uint8Array(J.length + 7 & -8);
  return z.set(J), z;
}

class qq {
  constructor(Q, J, Y, W, K) {
    this.bytes = Q, this.length = Y, this.context = W, this.get = K, this.bit = J % 8, this.byteIndex = J >> 3, this.byte = Q[this.byteIndex++], this.index = 0;
  }
  next() {
    if (this.index < this.length) {
      if (this.bit === 8)
        this.bit = 0, this.byte = this.bytes[this.byteIndex++];
      return {
        value: this.get(this.context, this.index++, this.byte, this.bit++)
      };
    }
    return { done: !0, value: null };
  }
  [Symbol.iterator]() {
    return this;
  }
}
function B3(Q, J, Y) {
  if (Y - J <= 0)
    return 0;
  if (Y - J < 8) {
    let z = 0;
    for (let N of new qq(Q, J, Y - J, Q, iM))
      z += N;
    return z;
  }
  let W = Y >> 3 << 3, K = J + (J % 8 === 0 ? 0 : 8 - J % 8);
  return B3(Q, J, K) + B3(Q, W, Y) + tM(Q, K >> 3, W - K >> 3);
}
function tM(Q, J, Y) {
  let W = 0, K = Math.trunc(J), z = new DataView(Q.buffer, Q.byteOffset, Q.byteLength), N = Y === void 0 ? Q.byteLength : K + Y;
  while (N - K >= 4)
    W += t5(z.getUint32(K)), K += 4;
  while (N - K >= 2)
    W += t5(z.getUint16(K)), K += 2;
  while (N - K >= 1)
    W += t5(z.getUint8(K)), K += 1;
  return W;
}
function t5(Q) {
  let J = Math.trunc(Q);
  return J = J - (J >>> 1 & 1431655765), J = (J & 858993459) + (J >>> 2 & 858993459), (J + (J >>> 4) & 252645135) * 16843009 >>> 24;
}

// node_modules/apache-arrow/data.mjs
var Ph = -1;

class d1 {
  constructor(Q, J, Y, W, K, z = [], N) {
    this.type = Q, this.children = z, this.dictionary = N, this.offset = Math.floor(Math.max(J || 0, 0)), this.length = Math.floor(Math.max(Y || 0, 0)), this._nullCount = Math.floor(Math.max(W || 0, -1));
    let F;
    if (K instanceof d1)
      this.stride = K.stride, this.values = K.values, this.typeIds = K.typeIds, this.nullBitmap = K.nullBitmap, this.valueOffsets = K.valueOffsets;
    else if (this.stride = JZ(Q), K)
      (F = K[0]) && (this.valueOffsets = F), (F = K[1]) && (this.values = F), (F = K[2]) && (this.nullBitmap = F), (F = K[3]) && (this.typeIds = F);
    this.nullable = this._nullCount !== 0 && this.nullBitmap && this.nullBitmap.byteLength > 0;
  }
  get typeId() {
    return this.type.typeId;
  }
  get ArrayType() {
    return this.type.ArrayType;
  }
  get buffers() {
    return [this.valueOffsets, this.values, this.nullBitmap, this.typeIds];
  }
  get byteLength() {
    let Q = 0, { valueOffsets: J, values: Y, nullBitmap: W, typeIds: K } = this;
    return J && (Q += J.byteLength), Y && (Q += Y.byteLength), W && (Q += W.byteLength), K && (Q += K.byteLength), this.children.reduce((z, N) => z + N.byteLength, Q);
  }
  get nullCount() {
    let Q = this._nullCount, J;
    if (Q <= Ph && (J = this.nullBitmap))
      this._nullCount = Q = this.length - B3(J, this.offset, this.offset + this.length);
    return Q;
  }
  getValid(Q) {
    if (this.nullable && this.nullCount > 0) {
      let J = this.offset + Q;
      return (this.nullBitmap[J >> 3] & 1 << J % 8) !== 0;
    }
    return !0;
  }
  setValid(Q, J) {
    if (!this.nullable)
      return J;
    if (!this.nullBitmap || this.nullBitmap.byteLength <= Q >> 3) {
      let { nullBitmap: F } = this._changeLengthAndBackfillNullBitmap(this.length);
      Object.assign(this, { nullBitmap: F, _nullCount: 0 });
    }
    let { nullBitmap: Y, offset: W } = this, K = W + Q >> 3, z = (W + Q) % 8, N = Y[K] >> z & 1;
    return J ? N === 0 && (Y[K] |= 1 << z, this._nullCount = this.nullCount + 1) : N === 1 && (Y[K] &= ~(1 << z), this._nullCount = this.nullCount - 1), J;
  }
  clone(Q = this.type, J = this.offset, Y = this.length, W = this._nullCount, K = this, z = this.children) {
    return new d1(Q, J, Y, W, K, z, this.dictionary);
  }
  slice(Q, J) {
    let { stride: Y, typeId: W, children: K } = this, z = +(this._nullCount === 0) - 1, N = W === 16 ? Y : 1, F = this._sliceBuffers(Q, J, Y, W);
    return this.clone(this.type, this.offset + Q, J, z, F, K.length === 0 || this.valueOffsets ? K : this._sliceChildren(K, N * Q, N * J));
  }
  _changeLengthAndBackfillNullBitmap(Q) {
    if (this.typeId === I.Null)
      return this.clone(this.type, 0, Q, 0);
    let { length: J, nullCount: Y } = this, W = new Uint8Array((Q + 63 & -64) >> 3).fill(255, 0, J >> 3);
    if (W[J >> 3] = (1 << J - (J & -8)) - 1, Y > 0)
      W.set(Yq(this.offset, J, this.nullBitmap), 0);
    let K = this.buffers;
    return K[wZ.VALIDITY] = W, this.clone(this.type, 0, Q, Y + (Q - J), K);
  }
  _sliceBuffers(Q, J, Y, W) {
    let K, { buffers: z } = this;
    return (K = z[wZ.TYPE]) && (z[wZ.TYPE] = K.subarray(Q, Q + J)), (K = z[wZ.OFFSET]) && (z[wZ.OFFSET] = K.subarray(Q, Q + J + 1)) || (K = z[wZ.DATA]) && (z[wZ.DATA] = W === 6 ? K : K.subarray(Y * Q, Y * (Q + J))), z;
  }
  _sliceChildren(Q, J, Y) {
    return Q.map((W) => W.slice(J, Y));
  }
}
d1.prototype.children = Object.freeze([]);

class C3 extends y0 {
  visit(Q) {
    return this.getVisitFn(Q.type).call(this, Q);
  }
  visitNull(Q) {
    let { ["type"]: J, ["offset"]: Y = 0, ["length"]: W = 0 } = Q;
    return new d1(J, Y, W, 0);
  }
  visitBool(Q) {
    let { ["type"]: J, ["offset"]: Y = 0 } = Q, W = n0(Q.nullBitmap), K = G1(J.ArrayType, Q.data), { ["length"]: z = K.length >> 3, ["nullCount"]: N = Q.nullBitmap ? -1 : 0 } = Q;
    return new d1(J, Y, z, N, [void 0, K, W]);
  }
  visitInt(Q) {
    let { ["type"]: J, ["offset"]: Y = 0 } = Q, W = n0(Q.nullBitmap), K = G1(J.ArrayType, Q.data), { ["length"]: z = K.length, ["nullCount"]: N = Q.nullBitmap ? -1 : 0 } = Q;
    return new d1(J, Y, z, N, [void 0, K, W]);
  }
  visitFloat(Q) {
    let { ["type"]: J, ["offset"]: Y = 0 } = Q, W = n0(Q.nullBitmap), K = G1(J.ArrayType, Q.data), { ["length"]: z = K.length, ["nullCount"]: N = Q.nullBitmap ? -1 : 0 } = Q;
    return new d1(J, Y, z, N, [void 0, K, W]);
  }
  visitUtf8(Q) {
    let { ["type"]: J, ["offset"]: Y = 0 } = Q, W = n0(Q.data), K = n0(Q.nullBitmap), z = k$(Q.valueOffsets), { ["length"]: N = z.length - 1, ["nullCount"]: F = Q.nullBitmap ? -1 : 0 } = Q;
    return new d1(J, Y, N, F, [z, W, K]);
  }
  visitBinary(Q) {
    let { ["type"]: J, ["offset"]: Y = 0 } = Q, W = n0(Q.data), K = n0(Q.nullBitmap), z = k$(Q.valueOffsets), { ["length"]: N = z.length - 1, ["nullCount"]: F = Q.nullBitmap ? -1 : 0 } = Q;
    return new d1(J, Y, N, F, [z, W, K]);
  }
  visitFixedSizeBinary(Q) {
    let { ["type"]: J, ["offset"]: Y = 0 } = Q, W = n0(Q.nullBitmap), K = G1(J.ArrayType, Q.data), { ["length"]: z = K.length / JZ(J), ["nullCount"]: N = Q.nullBitmap ? -1 : 0 } = Q;
    return new d1(J, Y, z, N, [void 0, K, W]);
  }
  visitDate(Q) {
    let { ["type"]: J, ["offset"]: Y = 0 } = Q, W = n0(Q.nullBitmap), K = G1(J.ArrayType, Q.data), { ["length"]: z = K.length / JZ(J), ["nullCount"]: N = Q.nullBitmap ? -1 : 0 } = Q;
    return new d1(J, Y, z, N, [void 0, K, W]);
  }
  visitTimestamp(Q) {
    let { ["type"]: J, ["offset"]: Y = 0 } = Q, W = n0(Q.nullBitmap), K = G1(J.ArrayType, Q.data), { ["length"]: z = K.length / JZ(J), ["nullCount"]: N = Q.nullBitmap ? -1 : 0 } = Q;
    return new d1(J, Y, z, N, [void 0, K, W]);
  }
  visitTime(Q) {
    let { ["type"]: J, ["offset"]: Y = 0 } = Q, W = n0(Q.nullBitmap), K = G1(J.ArrayType, Q.data), { ["length"]: z = K.length / JZ(J), ["nullCount"]: N = Q.nullBitmap ? -1 : 0 } = Q;
    return new d1(J, Y, z, N, [void 0, K, W]);
  }
  visitDecimal(Q) {
    let { ["type"]: J, ["offset"]: Y = 0 } = Q, W = n0(Q.nullBitmap), K = G1(J.ArrayType, Q.data), { ["length"]: z = K.length / JZ(J), ["nullCount"]: N = Q.nullBitmap ? -1 : 0 } = Q;
    return new d1(J, Y, z, N, [void 0, K, W]);
  }
  visitList(Q) {
    let { ["type"]: J, ["offset"]: Y = 0, ["child"]: W } = Q, K = n0(Q.nullBitmap), z = k$(Q.valueOffsets), { ["length"]: N = z.length - 1, ["nullCount"]: F = Q.nullBitmap ? -1 : 0 } = Q;
    return new d1(J, Y, N, F, [z, void 0, K], [W]);
  }
  visitStruct(Q) {
    let { ["type"]: J, ["offset"]: Y = 0, ["children"]: W = [] } = Q, K = n0(Q.nullBitmap), { length: z = W.reduce((F, { length: L }) => Math.max(F, L), 0), nullCount: N = Q.nullBitmap ? -1 : 0 } = Q;
    return new d1(J, Y, z, N, [void 0, void 0, K], W);
  }
  visitUnion(Q) {
    let { ["type"]: J, ["offset"]: Y = 0, ["children"]: W = [] } = Q, K = n0(Q.nullBitmap), z = G1(J.ArrayType, Q.typeIds), { ["length"]: N = z.length, ["nullCount"]: F = Q.nullBitmap ? -1 : 0 } = Q;
    if (C0.isSparseUnion(J))
      return new d1(J, Y, N, F, [void 0, void 0, K, z], W);
    let L = k$(Q.valueOffsets);
    return new d1(J, Y, N, F, [L, void 0, K, z], W);
  }
  visitDictionary(Q) {
    let { ["type"]: J, ["offset"]: Y = 0 } = Q, W = n0(Q.nullBitmap), K = G1(J.indices.ArrayType, Q.data), { ["dictionary"]: z = new Z1([new C3().visit({ type: J.dictionary })]) } = Q, { ["length"]: N = K.length, ["nullCount"]: F = Q.nullBitmap ? -1 : 0 } = Q;
    return new d1(J, Y, N, F, [void 0, K, W], [], z);
  }
  visitInterval(Q) {
    let { ["type"]: J, ["offset"]: Y = 0 } = Q, W = n0(Q.nullBitmap), K = G1(J.ArrayType, Q.data), { ["length"]: z = K.length / JZ(J), ["nullCount"]: N = Q.nullBitmap ? -1 : 0 } = Q;
    return new d1(J, Y, z, N, [void 0, K, W]);
  }
  visitFixedSizeList(Q) {
    let { ["type"]: J, ["offset"]: Y = 0, ["child"]: W = new C3().visit({ type: J.valueType }) } = Q, K = n0(Q.nullBitmap), { ["length"]: z = W.length / JZ(J), ["nullCount"]: N = Q.nullBitmap ? -1 : 0 } = Q;
    return new d1(J, Y, z, N, [void 0, void 0, K], [W]);
  }
  visitMap(Q) {
    let { ["type"]: J, ["offset"]: Y = 0, ["child"]: W = new C3().visit({ type: J.childType }) } = Q, K = n0(Q.nullBitmap), z = k$(Q.valueOffsets), { ["length"]: N = z.length - 1, ["nullCount"]: F = Q.nullBitmap ? -1 : 0 } = Q;
    return new d1(J, Y, N, F, [z, void 0, K], [W]);
  }
}
function e0(Q) {
  return new C3().visit(Q);
}

// node_modules/apache-arrow/util/chunk.mjs
class QH {
  constructor(Q = 0, J) {
    this.numChunks = Q, this.getChunkIterator = J, this.chunkIndex = 0, this.chunkIterator = this.getChunkIterator(0);
  }
  next() {
    while (this.chunkIndex < this.numChunks) {
      let Q = this.chunkIterator.next();
      if (!Q.done)
        return Q;
      if (++this.chunkIndex < this.numChunks)
        this.chunkIterator = this.getChunkIterator(this.chunkIndex);
    }
    return { done: !0, value: null };
  }
  [Symbol.iterator]() {
    return this;
  }
}
function ZH(Q) {
  return Q.reduce((J, Y) => J + Y.nullCount, 0);
}
function XH(Q) {
  return Q.reduce((J, Y, W) => {
    return J[W + 1] = J[W] + Y.length, J;
  }, new Uint32Array(Q.length + 1));
}
function JH(Q, J, Y, W) {
  let K = [];
  for (let z = -1, N = Q.length;++z < N; ) {
    let F = Q[z], L = J[z], { length: w } = F;
    if (L >= W)
      break;
    if (Y >= L + w)
      continue;
    if (L >= Y && L + w <= W) {
      K.push(F);
      continue;
    }
    let D = Math.max(0, Y - L), R = Math.min(W - L, w);
    K.push(F.slice(D, R - D));
  }
  if (K.length === 0)
    K.push(Q[0].slice(0, 0));
  return K;
}
function tN(Q, J, Y, W) {
  let K = 0, z = 0, N = J.length - 1;
  do {
    if (K >= N - 1)
      return Y < J[N] ? W(Q, K, Y - J[K]) : null;
    z = K + Math.trunc((N - K) * 0.5), Y < J[z] ? N = z : K = z;
  } while (K < N);
}
function V3(Q, J) {
  return Q.getValid(J);
}
function OJ(Q) {
  function J(Y, W, K) {
    return Q(Y[W], K);
  }
  return function(Y) {
    let W = this.data;
    return tN(W, this._offsets, Y, J);
  };
}
function $H(Q) {
  let J;
  function Y(W, K, z) {
    return Q(W[K], z, J);
  }
  return function(W, K) {
    let z = this.data;
    J = K;
    let N = tN(z, this._offsets, W, Y);
    return J = void 0, N;
  };
}
function YH(Q) {
  let J;
  function Y(W, K, z) {
    let N = z, F = 0, L = 0;
    for (let w = K - 1, D = W.length;++w < D; ) {
      let R = W[w];
      if (~(F = Q(R, J, N)))
        return L + F;
      N = 0, L += R.length;
    }
    return -1;
  }
  return function(W, K) {
    J = W;
    let z = this.data, N = typeof K !== "number" ? Y(z, 0, 0) : tN(z, this._offsets, K, Y);
    return J = void 0, N;
  };
}

// node_modules/apache-arrow/visitor/indexof.mjs
class o0 extends y0 {
}
function Ah(Q, J) {
  return J === null && Q.length > 0 ? 0 : -1;
}
function Lh(Q, J) {
  let { nullBitmap: Y } = Q;
  if (!Y || Q.nullCount <= 0)
    return -1;
  let W = 0;
  for (let K of new qq(Y, Q.offset + (J || 0), Q.length, Y, e5)) {
    if (!K)
      return W;
    ++W;
  }
  return -1;
}
function z1(Q, J, Y) {
  if (J === void 0)
    return -1;
  if (J === null)
    return Lh(Q, Y);
  let W = c6.getVisitFn(Q), K = LJ(J);
  for (let z = (Y || 0) - 1, N = Q.length;++z < N; )
    if (K(W(Q, z)))
      return z;
  return -1;
}
function eM(Q, J, Y) {
  let W = c6.getVisitFn(Q), K = LJ(J);
  for (let z = (Y || 0) - 1, N = Q.length;++z < N; )
    if (K(W(Q, z)))
      return z;
  return -1;
}
o0.prototype.visitNull = Ah;
o0.prototype.visitBool = z1;
o0.prototype.visitInt = z1;
o0.prototype.visitInt8 = z1;
o0.prototype.visitInt16 = z1;
o0.prototype.visitInt32 = z1;
o0.prototype.visitInt64 = z1;
o0.prototype.visitUint8 = z1;
o0.prototype.visitUint16 = z1;
o0.prototype.visitUint32 = z1;
o0.prototype.visitUint64 = z1;
o0.prototype.visitFloat = z1;
o0.prototype.visitFloat16 = z1;
o0.prototype.visitFloat32 = z1;
o0.prototype.visitFloat64 = z1;
o0.prototype.visitUtf8 = z1;
o0.prototype.visitBinary = z1;
o0.prototype.visitFixedSizeBinary = z1;
o0.prototype.visitDate = z1;
o0.prototype.visitDateDay = z1;
o0.prototype.visitDateMillisecond = z1;
o0.prototype.visitTimestamp = z1;
o0.prototype.visitTimestampSecond = z1;
o0.prototype.visitTimestampMillisecond = z1;
o0.prototype.visitTimestampMicrosecond = z1;
o0.prototype.visitTimestampNanosecond = z1;
o0.prototype.visitTime = z1;
o0.prototype.visitTimeSecond = z1;
o0.prototype.visitTimeMillisecond = z1;
o0.prototype.visitTimeMicrosecond = z1;
o0.prototype.visitTimeNanosecond = z1;
o0.prototype.visitDecimal = z1;
o0.prototype.visitList = z1;
o0.prototype.visitStruct = z1;
o0.prototype.visitUnion = z1;
o0.prototype.visitDenseUnion = eM;
o0.prototype.visitSparseUnion = eM;
o0.prototype.visitDictionary = z1;
o0.prototype.visitInterval = z1;
o0.prototype.visitIntervalDayTime = z1;
o0.prototype.visitIntervalYearMonth = z1;
o0.prototype.visitFixedSizeList = z1;
o0.prototype.visitMap = z1;
var B$ = new o0;

// node_modules/apache-arrow/visitor/iterator.mjs
class a0 extends y0 {
}
function J1(Q) {
  let { type: J } = Q;
  if (Q.nullCount === 0 && Q.stride === 1 && (J.typeId === I.Timestamp || J instanceof u6 && J.bitWidth !== 64 || J instanceof yX && J.bitWidth !== 64 || J instanceof XZ && J.precision !== K6.HALF))
    return new QH(Q.data.length, (W) => {
      let K = Q.data[W];
      return K.values.subarray(0, K.length)[Symbol.iterator]();
    });
  let Y = 0;
  return new QH(Q.data.length, (W) => {
    let z = Q.data[W].length, N = Q.slice(Y, Y + z);
    return Y += z, new QD(N);
  });
}

class QD {
  constructor(Q) {
    this.vector = Q, this.index = 0;
  }
  next() {
    if (this.index < this.vector.length)
      return {
        value: this.vector.get(this.index++)
      };
    return { done: !0, value: null };
  }
  [Symbol.iterator]() {
    return this;
  }
}
a0.prototype.visitNull = J1;
a0.prototype.visitBool = J1;
a0.prototype.visitInt = J1;
a0.prototype.visitInt8 = J1;
a0.prototype.visitInt16 = J1;
a0.prototype.visitInt32 = J1;
a0.prototype.visitInt64 = J1;
a0.prototype.visitUint8 = J1;
a0.prototype.visitUint16 = J1;
a0.prototype.visitUint32 = J1;
a0.prototype.visitUint64 = J1;
a0.prototype.visitFloat = J1;
a0.prototype.visitFloat16 = J1;
a0.prototype.visitFloat32 = J1;
a0.prototype.visitFloat64 = J1;
a0.prototype.visitUtf8 = J1;
a0.prototype.visitBinary = J1;
a0.prototype.visitFixedSizeBinary = J1;
a0.prototype.visitDate = J1;
a0.prototype.visitDateDay = J1;
a0.prototype.visitDateMillisecond = J1;
a0.prototype.visitTimestamp = J1;
a0.prototype.visitTimestampSecond = J1;
a0.prototype.visitTimestampMillisecond = J1;
a0.prototype.visitTimestampMicrosecond = J1;
a0.prototype.visitTimestampNanosecond = J1;
a0.prototype.visitTime = J1;
a0.prototype.visitTimeSecond = J1;
a0.prototype.visitTimeMillisecond = J1;
a0.prototype.visitTimeMicrosecond = J1;
a0.prototype.visitTimeNanosecond = J1;
a0.prototype.visitDecimal = J1;
a0.prototype.visitList = J1;
a0.prototype.visitStruct = J1;
a0.prototype.visitUnion = J1;
a0.prototype.visitDenseUnion = J1;
a0.prototype.visitSparseUnion = J1;
a0.prototype.visitDictionary = J1;
a0.prototype.visitInterval = J1;
a0.prototype.visitIntervalDayTime = J1;
a0.prototype.visitIntervalYearMonth = J1;
a0.prototype.visitFixedSizeList = J1;
a0.prototype.visitMap = J1;
var Wq = new a0;

// node_modules/apache-arrow/visitor/bytelength.mjs
var Oh = (Q, J) => Q + J;

class M4 extends y0 {
  visitNull(Q, J) {
    return 0;
  }
  visitInt(Q, J) {
    return Q.type.bitWidth / 8;
  }
  visitFloat(Q, J) {
    return Q.type.ArrayType.BYTES_PER_ELEMENT;
  }
  visitBool(Q, J) {
    return 0.125;
  }
  visitDecimal(Q, J) {
    return Q.type.bitWidth / 8;
  }
  visitDate(Q, J) {
    return (Q.type.unit + 1) * 4;
  }
  visitTime(Q, J) {
    return Q.type.bitWidth / 8;
  }
  visitTimestamp(Q, J) {
    return Q.type.unit === F1.SECOND ? 4 : 8;
  }
  visitInterval(Q, J) {
    return (Q.type.unit + 1) * 4;
  }
  visitStruct(Q, J) {
    return Q.children.reduce((Y, W) => Y + $Z.visit(W, J), 0);
  }
  visitFixedSizeBinary(Q, J) {
    return Q.type.byteWidth;
  }
  visitMap(Q, J) {
    return 8 + Q.children.reduce((Y, W) => Y + $Z.visit(W, J), 0);
  }
  visitDictionary(Q, J) {
    var Y;
    return Q.type.indices.bitWidth / 8 + (((Y = Q.dictionary) === null || Y === void 0 ? void 0 : Y.getByteLength(Q.values[J])) || 0);
  }
}
var wh = ({ valueOffsets: Q }, J) => {
  return 8 + (Q[J + 1] - Q[J]);
}, Mh = ({ valueOffsets: Q }, J) => {
  return 8 + (Q[J + 1] - Q[J]);
}, Dh = ({ valueOffsets: Q, stride: J, children: Y }, W) => {
  let K = Y[0], { [W * J]: z } = Q, { [W * J + 1]: N } = Q, F = $Z.getVisitFn(K.type), L = K.slice(z, N - z), w = 8;
  for (let D = -1, R = N - z;++D < R; )
    w += F(L, D);
  return w;
}, kh = ({ stride: Q, children: J }, Y) => {
  let W = J[0], K = W.slice(Y * Q, Q), z = $Z.getVisitFn(W.type), N = 0;
  for (let F = -1, L = K.length;++F < L; )
    N += z(K, F);
  return N;
}, Rh = (Q, J) => {
  return Q.type.mode === k6.Dense ? ZD(Q, J) : XD(Q, J);
}, ZD = ({ type: Q, children: J, typeIds: Y, valueOffsets: W }, K) => {
  let z = Q.typeIdToChildIndex[Y[K]];
  return 8 + $Z.visit(J[z], W[K]);
}, XD = ({ children: Q }, J) => {
  return 4 + $Z.visitMany(Q, Q.map(() => J)).reduce(Oh, 0);
};
M4.prototype.visitUtf8 = wh;
M4.prototype.visitBinary = Mh;
M4.prototype.visitList = Dh;
M4.prototype.visitFixedSizeList = kh;
M4.prototype.visitUnion = Rh;
M4.prototype.visitDenseUnion = ZD;
M4.prototype.visitSparseUnion = XD;
var $Z = new M4;

// node_modules/apache-arrow/vector.mjs
var JD, $D = {}, YD = {};

class Z1 {
  constructor(Q) {
    var J, Y, W;
    let K = Q[0] instanceof Z1 ? Q.flatMap((N) => N.data) : Q;
    if (K.length === 0 || K.some((N) => !(N instanceof d1)))
      throw new TypeError("Vector constructor expects an Array of Data instances.");
    let z = (J = K[0]) === null || J === void 0 ? void 0 : J.type;
    switch (K.length) {
      case 0:
        this._offsets = [0];
        break;
      case 1: {
        let { get: N, set: F, indexOf: L, byteLength: w } = $D[z.typeId], D = K[0];
        this.isValid = (R) => V3(D, R), this.get = (R) => N(D, R), this.set = (R, V) => F(D, R, V), this.indexOf = (R) => L(D, R), this.getByteLength = (R) => w(D, R), this._offsets = [0, D.length];
        break;
      }
      default:
        Object.setPrototypeOf(this, YD[z.typeId]), this._offsets = XH(K);
        break;
    }
    this.data = K, this.type = z, this.stride = JZ(z), this.numChildren = (W = (Y = z.children) === null || Y === void 0 ? void 0 : Y.length) !== null && W !== void 0 ? W : 0, this.length = this._offsets[this._offsets.length - 1];
  }
  get byteLength() {
    if (this._byteLength === -1)
      this._byteLength = this.data.reduce((Q, J) => Q + J.byteLength, 0);
    return this._byteLength;
  }
  get nullCount() {
    if (this._nullCount === -1)
      this._nullCount = ZH(this.data);
    return this._nullCount;
  }
  get ArrayType() {
    return this.type.ArrayType;
  }
  get [Symbol.toStringTag]() {
    return `${this.VectorName}<${this.type[Symbol.toStringTag]}>`;
  }
  get VectorName() {
    return `${I[this.type.typeId]}Vector`;
  }
  isValid(Q) {
    return !1;
  }
  get(Q) {
    return null;
  }
  set(Q, J) {
    return;
  }
  indexOf(Q, J) {
    return -1;
  }
  includes(Q, J) {
    return this.indexOf(Q, J) > 0;
  }
  getByteLength(Q) {
    return 0;
  }
  [Symbol.iterator]() {
    return Wq.visit(this);
  }
  concat(...Q) {
    return new Z1(this.data.concat(Q.flatMap((J) => J.data).flat(Number.POSITIVE_INFINITY)));
  }
  slice(Q, J) {
    return new Z1(j3(this, Q, J, ({ data: Y, _offsets: W }, K, z) => JH(Y, W, K, z)));
  }
  toJSON() {
    return [...this];
  }
  toArray() {
    let { type: Q, data: J, length: Y, stride: W, ArrayType: K } = this;
    switch (Q.typeId) {
      case I.Int:
      case I.Float:
      case I.Decimal:
      case I.Time:
      case I.Timestamp:
        switch (J.length) {
          case 0:
            return new K;
          case 1:
            return J[0].values.subarray(0, Y * W);
          default:
            return J.reduce((z, { values: N, length: F }) => {
              return z.array.set(N.subarray(0, F * W), z.offset), z.offset += F * W, z;
            }, { array: new K(Y * W), offset: 0 }).array;
        }
    }
    return [...this];
  }
  toString() {
    return `[${[...this].join(",")}]`;
  }
  getChild(Q) {
    var J;
    return this.getChildAt((J = this.type.children) === null || J === void 0 ? void 0 : J.findIndex((Y) => Y.name === Q));
  }
  getChildAt(Q) {
    if (Q > -1 && Q < this.numChildren)
      return new Z1(this.data.map(({ children: J }) => J[Q]));
    return null;
  }
  get isMemoized() {
    if (C0.isDictionary(this.type))
      return this.data[0].dictionary.isMemoized;
    return !1;
  }
  memoize() {
    if (C0.isDictionary(this.type)) {
      let Q = new qH(this.data[0].dictionary), J = this.data.map((Y) => {
        let W = Y.clone();
        return W.dictionary = Q, W;
      });
      return new Z1(J);
    }
    return new qH(this);
  }
  unmemoize() {
    if (C0.isDictionary(this.type) && this.isMemoized) {
      let Q = this.data[0].dictionary.unmemoize(), J = this.data.map((Y) => {
        let W = Y.clone();
        return W.dictionary = Q, W;
      });
      return new Z1(J);
    }
    return this;
  }
}
JD = Symbol.toStringTag;
Z1[JD] = ((Q) => {
  Q.type = C0.prototype, Q.data = [], Q.length = 0, Q.stride = 1, Q.numChildren = 0, Q._nullCount = -1, Q._byteLength = -1, Q._offsets = new Uint32Array([0]), Q[Symbol.isConcatSpreadable] = !0;
  let J = Object.keys(I).map((Y) => I[Y]).filter((Y) => typeof Y === "number" && Y !== I.NONE);
  for (let Y of J) {
    let W = c6.getVisitFnByTypeId(Y), K = m8.getVisitFnByTypeId(Y), z = B$.getVisitFnByTypeId(Y), N = $Z.getVisitFnByTypeId(Y);
    $D[Y] = { get: W, set: K, indexOf: z, byteLength: N }, YD[Y] = Object.create(Q, {
      ["isValid"]: { value: OJ(V3) },
      ["get"]: { value: OJ(c6.getVisitFnByTypeId(Y)) },
      ["set"]: { value: $H(m8.getVisitFnByTypeId(Y)) },
      ["indexOf"]: { value: YH(B$.getVisitFnByTypeId(Y)) },
      ["getByteLength"]: { value: OJ($Z.getVisitFnByTypeId(Y)) }
    });
  }
  return "Vector";
})(Z1.prototype);

class qH extends Z1 {
  constructor(Q) {
    super(Q.data);
    let J = this.get, Y = this.set, W = this.slice, K = new Array(this.length);
    Object.defineProperty(this, "get", {
      value(z) {
        let N = K[z];
        if (N !== void 0)
          return N;
        let F = J.call(this, z);
        return K[z] = F, F;
      }
    }), Object.defineProperty(this, "set", {
      value(z, N) {
        Y.call(this, z, N), K[z] = N;
      }
    }), Object.defineProperty(this, "slice", {
      value: (z, N) => new qH(W.call(this, z, N))
    }), Object.defineProperty(this, "isMemoized", { value: !0 }), Object.defineProperty(this, "unmemoize", {
      value: () => new Z1(this.data)
    }), Object.defineProperty(this, "memoize", {
      value: () => this
    });
  }
}

// node_modules/apache-arrow/builder/valid.mjs
function qD(Q) {
  if (!Q || Q.length <= 0)
    return function W(K) {
      return !0;
    };
  let J = "", Y = Q.filter((W) => W === W);
  if (Y.length > 0)
    J = `
    switch (x) {${Y.map((W) => `
        case ${jh(W)}:`).join("")}
            return false;
    }`;
  if (Q.length !== Y.length)
    J = `if (x !== x) return false;
${J}`;
  return new Function("x", `${J}
return true;`);
}
function jh(Q) {
  if (typeof Q !== "bigint")
    return $X(Q);
  else if (S5)
    return `${$X(Q)}n`;
  return `"${$X(Q)}"`;
}

// node_modules/apache-arrow/builder/buffer.mjs
var eN = (Q, J) => (Math.ceil(Q) * J + 63 & -64 || 64) / J, Bh = (Q, J = 0) => Q.length >= J ? Q.subarray(0, J) : tY(new Q.constructor(J), Q, 0);

class C$ {
  constructor(Q, J = 1) {
    this.buffer = Q, this.stride = J, this.BYTES_PER_ELEMENT = Q.BYTES_PER_ELEMENT, this.ArrayType = Q.constructor, this._resize(this.length = Math.ceil(Q.length / J));
  }
  get byteLength() {
    return Math.ceil(this.length * this.stride) * this.BYTES_PER_ELEMENT;
  }
  get reservedLength() {
    return this.buffer.length / this.stride;
  }
  get reservedByteLength() {
    return this.buffer.byteLength;
  }
  set(Q, J) {
    return this;
  }
  append(Q) {
    return this.set(this.length, Q);
  }
  reserve(Q) {
    if (Q > 0) {
      this.length += Q;
      let J = this.stride, Y = this.length * J, W = this.buffer.length;
      if (Y >= W)
        this._resize(W === 0 ? eN(Y * 1, this.BYTES_PER_ELEMENT) : eN(Y * 2, this.BYTES_PER_ELEMENT));
    }
    return this;
  }
  flush(Q = this.length) {
    Q = eN(Q * this.stride, this.BYTES_PER_ELEMENT);
    let J = Bh(this.buffer, Q);
    return this.clear(), J;
  }
  clear() {
    return this.length = 0, this._resize(0), this;
  }
  _resize(Q) {
    return this.buffer = tY(new this.ArrayType(Q), this.buffer);
  }
}
C$.prototype.offset = 0;

class wJ extends C$ {
  last() {
    return this.get(this.length - 1);
  }
  get(Q) {
    return this.buffer[Q];
  }
  set(Q, J) {
    return this.reserve(Q - this.length + 1), this.buffer[Q * this.stride] = J, this;
  }
}

class S3 extends wJ {
  constructor(Q = new Uint8Array(0)) {
    super(Q, 0.125);
    this.numValid = 0;
  }
  get numInvalid() {
    return this.length - this.numValid;
  }
  get(Q) {
    return this.buffer[Q >> 3] >> Q % 8 & 1;
  }
  set(Q, J) {
    let { buffer: Y } = this.reserve(Q - this.length + 1), W = Q >> 3, K = Q % 8, z = Y[W] >> K & 1;
    return J ? z === 0 && (Y[W] |= 1 << K, ++this.numValid) : z === 1 && (Y[W] &= ~(1 << K), --this.numValid), this;
  }
  clear() {
    return this.numValid = 0, super.clear();
  }
}

class I3 extends wJ {
  constructor(Q = new Int32Array(1)) {
    super(Q, 1);
  }
  append(Q) {
    return this.set(this.length - 1, Q);
  }
  set(Q, J) {
    let Y = this.length - 1, W = this.reserve(Q - Y + 1).buffer;
    if (Y < Q++)
      W.fill(W[Y], Y, Q);
    return W[Q] = W[Q - 1] + J, this;
  }
  flush(Q = this.length - 1) {
    if (Q > this.length)
      this.set(Q - 1, 0);
    return super.flush(Q + 1);
  }
}

// node_modules/apache-arrow/builder.mjs
class U6 {
  constructor({ type: Q, nullValues: J }) {
    if (this.length = 0, this.finished = !1, this.type = Q, this.children = [], this.nullValues = J, this.stride = JZ(Q), this._nulls = new S3, J && J.length > 0)
      this._isValid = qD(J);
  }
  static throughNode(Q) {
    throw new Error('"throughNode" not available in this environment');
  }
  static throughDOM(Q) {
    throw new Error('"throughDOM" not available in this environment');
  }
  toVector() {
    return new Z1([this.flush()]);
  }
  get ArrayType() {
    return this.type.ArrayType;
  }
  get nullCount() {
    return this._nulls.numInvalid;
  }
  get numChildren() {
    return this.children.length;
  }
  get byteLength() {
    let Q = 0, { _offsets: J, _values: Y, _nulls: W, _typeIds: K, children: z } = this;
    return J && (Q += J.byteLength), Y && (Q += Y.byteLength), W && (Q += W.byteLength), K && (Q += K.byteLength), z.reduce((N, F) => N + F.byteLength, Q);
  }
  get reservedLength() {
    return this._nulls.reservedLength;
  }
  get reservedByteLength() {
    let Q = 0;
    return this._offsets && (Q += this._offsets.reservedByteLength), this._values && (Q += this._values.reservedByteLength), this._nulls && (Q += this._nulls.reservedByteLength), this._typeIds && (Q += this._typeIds.reservedByteLength), this.children.reduce((J, Y) => J + Y.reservedByteLength, Q);
  }
  get valueOffsets() {
    return this._offsets ? this._offsets.buffer : null;
  }
  get values() {
    return this._values ? this._values.buffer : null;
  }
  get nullBitmap() {
    return this._nulls ? this._nulls.buffer : null;
  }
  get typeIds() {
    return this._typeIds ? this._typeIds.buffer : null;
  }
  append(Q) {
    return this.set(this.length, Q);
  }
  isValid(Q) {
    return this._isValid(Q);
  }
  set(Q, J) {
    if (this.setValid(Q, this.isValid(J)))
      this.setValue(Q, J);
    return this;
  }
  setValue(Q, J) {
    this._setValue(this, Q, J);
  }
  setValid(Q, J) {
    return this.length = this._nulls.set(Q, +J).length, J;
  }
  addChild(Q, J = `${this.numChildren}`) {
    throw new Error(`Cannot append children to non-nested type "${this.type}"`);
  }
  getChildAt(Q) {
    return this.children[Q] || null;
  }
  flush() {
    let Q, J, Y, W, { type: K, length: z, nullCount: N, _typeIds: F, _offsets: L, _values: w, _nulls: D } = this;
    if (J = F === null || F === void 0 ? void 0 : F.flush(z))
      W = L === null || L === void 0 ? void 0 : L.flush(z);
    else if (W = L === null || L === void 0 ? void 0 : L.flush(z))
      Q = w === null || w === void 0 ? void 0 : w.flush(L.last());
    else
      Q = w === null || w === void 0 ? void 0 : w.flush(z);
    if (N > 0)
      Y = D === null || D === void 0 ? void 0 : D.flush(z);
    let R = this.children.map((V) => V.flush());
    return this.clear(), e0({
      type: K,
      length: z,
      nullCount: N,
      children: R,
      child: R[0],
      data: Q,
      typeIds: J,
      nullBitmap: Y,
      valueOffsets: W
    });
  }
  finish() {
    this.finished = !0;
    for (let Q of this.children)
      Q.finish();
    return this;
  }
  clear() {
    var Q, J, Y, W;
    this.length = 0, (Q = this._nulls) === null || Q === void 0 || Q.clear(), (J = this._values) === null || J === void 0 || J.clear(), (Y = this._offsets) === null || Y === void 0 || Y.clear(), (W = this._typeIds) === null || W === void 0 || W.clear();
    for (let K of this.children)
      K.clear();
    return this;
  }
}
U6.prototype.length = 1;
U6.prototype.stride = 1;
U6.prototype.children = null;
U6.prototype.finished = !1;
U6.prototype.nullValues = null;
U6.prototype._isValid = () => !0;

class b8 extends U6 {
  constructor(Q) {
    super(Q);
    this._values = new wJ(new this.ArrayType(0), this.stride);
  }
  setValue(Q, J) {
    let Y = this._values;
    return Y.reserve(Q - Y.length + 1), super.setValue(Q, J);
  }
}

class D4 extends U6 {
  constructor(Q) {
    super(Q);
    this._pendingLength = 0, this._offsets = new I3;
  }
  setValue(Q, J) {
    let Y = this._pending || (this._pending = /* @__PURE__ */ new Map), W = Y.get(Q);
    W && (this._pendingLength -= W.length), this._pendingLength += J instanceof w4 ? J[DZ].length : J.length, Y.set(Q, J);
  }
  setValid(Q, J) {
    if (!super.setValid(Q, J))
      return (this._pending || (this._pending = /* @__PURE__ */ new Map)).set(Q, void 0), !1;
    return !0;
  }
  clear() {
    return this._pendingLength = 0, this._pending = void 0, super.clear();
  }
  flush() {
    return this._flush(), super.flush();
  }
  finish() {
    return this._flush(), super.finish();
  }
  _flush() {
    let Q = this._pending, J = this._pendingLength;
    if (this._pendingLength = 0, this._pending = void 0, Q && Q.size > 0)
      this._flushPending(Q, J);
    return this;
  }
}

// node_modules/apache-arrow/fb/block.mjs
class Kq {
  constructor() {
    this.bb = null, this.bb_pos = 0;
  }
  __init(Q, J) {
    return this.bb_pos = Q, this.bb = J, this;
  }
  offset() {
    return this.bb.readInt64(this.bb_pos);
  }
  metaDataLength() {
    return this.bb.readInt32(this.bb_pos + 8);
  }
  bodyLength() {
    return this.bb.readInt64(this.bb_pos + 16);
  }
  static sizeOf() {
    return 24;
  }
  static createBlock(Q, J, Y, W) {
    return Q.prep(8, 24), Q.writeInt64(W), Q.pad(4), Q.writeInt32(Y), Q.writeInt64(J), Q.offset();
  }
}

// node_modules/flatbuffers/mjs/constants.js
var _3 = 2, YZ = 4, kZ = 4, R0 = 4;
// node_modules/flatbuffers/mjs/utils.js
var cX = new Int32Array(2), WH = new Float32Array(cX.buffer), KH = new Float64Array(cX.buffer), Hq = new Uint16Array(new Uint8Array([1, 0]).buffer)[0] === 1;
// node_modules/flatbuffers/mjs/long.js
class L8 {
  constructor(Q, J) {
    this.low = Q | 0, this.high = J | 0;
  }
  static create(Q, J) {
    return Q == 0 && J == 0 ? L8.ZERO : new L8(Q, J);
  }
  toFloat64() {
    return (this.low >>> 0) + this.high * 4294967296;
  }
  equals(Q) {
    return this.low == Q.low && this.high == Q.high;
  }
}
L8.ZERO = new L8(0, 0);
// node_modules/flatbuffers/mjs/encoding.js
var T3;
(function(Q) {
  Q[Q.UTF8_BYTES = 1] = "UTF8_BYTES", Q[Q.UTF16_STRING = 2] = "UTF16_STRING";
})(T3 || (T3 = {}));
// node_modules/flatbuffers/mjs/byte-buffer.js
class qZ {
  constructor(Q) {
    this.bytes_ = Q, this.position_ = 0;
  }
  static allocate(Q) {
    return new qZ(new Uint8Array(Q));
  }
  clear() {
    this.position_ = 0;
  }
  bytes() {
    return this.bytes_;
  }
  position() {
    return this.position_;
  }
  setPosition(Q) {
    this.position_ = Q;
  }
  capacity() {
    return this.bytes_.length;
  }
  readInt8(Q) {
    return this.readUint8(Q) << 24 >> 24;
  }
  readUint8(Q) {
    return this.bytes_[Q];
  }
  readInt16(Q) {
    return this.readUint16(Q) << 16 >> 16;
  }
  readUint16(Q) {
    return this.bytes_[Q] | this.bytes_[Q + 1] << 8;
  }
  readInt32(Q) {
    return this.bytes_[Q] | this.bytes_[Q + 1] << 8 | this.bytes_[Q + 2] << 16 | this.bytes_[Q + 3] << 24;
  }
  readUint32(Q) {
    return this.readInt32(Q) >>> 0;
  }
  readInt64(Q) {
    return new L8(this.readInt32(Q), this.readInt32(Q + 4));
  }
  readUint64(Q) {
    return new L8(this.readUint32(Q), this.readUint32(Q + 4));
  }
  readFloat32(Q) {
    return cX[0] = this.readInt32(Q), WH[0];
  }
  readFloat64(Q) {
    return cX[Hq ? 0 : 1] = this.readInt32(Q), cX[Hq ? 1 : 0] = this.readInt32(Q + 4), KH[0];
  }
  writeInt8(Q, J) {
    this.bytes_[Q] = J;
  }
  writeUint8(Q, J) {
    this.bytes_[Q] = J;
  }
  writeInt16(Q, J) {
    this.bytes_[Q] = J, this.bytes_[Q + 1] = J >> 8;
  }
  writeUint16(Q, J) {
    this.bytes_[Q] = J, this.bytes_[Q + 1] = J >> 8;
  }
  writeInt32(Q, J) {
    this.bytes_[Q] = J, this.bytes_[Q + 1] = J >> 8, this.bytes_[Q + 2] = J >> 16, this.bytes_[Q + 3] = J >> 24;
  }
  writeUint32(Q, J) {
    this.bytes_[Q] = J, this.bytes_[Q + 1] = J >> 8, this.bytes_[Q + 2] = J >> 16, this.bytes_[Q + 3] = J >> 24;
  }
  writeInt64(Q, J) {
    this.writeInt32(Q, J.low), this.writeInt32(Q + 4, J.high);
  }
  writeUint64(Q, J) {
    this.writeUint32(Q, J.low), this.writeUint32(Q + 4, J.high);
  }
  writeFloat32(Q, J) {
    WH[0] = J, this.writeInt32(Q, cX[0]);
  }
  writeFloat64(Q, J) {
    KH[0] = J, this.writeInt32(Q, cX[Hq ? 0 : 1]), this.writeInt32(Q + 4, cX[Hq ? 1 : 0]);
  }
  getBufferIdentifier() {
    if (this.bytes_.length < this.position_ + YZ + kZ)
      throw new Error("FlatBuffers: ByteBuffer is too short to contain an identifier.");
    let Q = "";
    for (let J = 0;J < kZ; J++)
      Q += String.fromCharCode(this.readInt8(this.position_ + YZ + J));
    return Q;
  }
  __offset(Q, J) {
    let Y = Q - this.readInt32(Q);
    return J < this.readInt16(Y) ? this.readInt16(Y + J) : 0;
  }
  __union(Q, J) {
    return Q.bb_pos = J + this.readInt32(J), Q.bb = this, Q;
  }
  __string(Q, J) {
    Q += this.readInt32(Q);
    let Y = this.readInt32(Q), W = "", K = 0;
    if (Q += YZ, J === T3.UTF8_BYTES)
      return this.bytes_.subarray(Q, Q + Y);
    while (K < Y) {
      let z, N = this.readUint8(Q + K++);
      if (N < 192)
        z = N;
      else {
        let F = this.readUint8(Q + K++);
        if (N < 224)
          z = (N & 31) << 6 | F & 63;
        else {
          let L = this.readUint8(Q + K++);
          if (N < 240)
            z = (N & 15) << 12 | (F & 63) << 6 | L & 63;
          else {
            let w = this.readUint8(Q + K++);
            z = (N & 7) << 18 | (F & 63) << 12 | (L & 63) << 6 | w & 63;
          }
        }
      }
      if (z < 65536)
        W += String.fromCharCode(z);
      else
        z -= 65536, W += String.fromCharCode((z >> 10) + 55296, (z & 1023) + 56320);
    }
    return W;
  }
  __union_with_string(Q, J) {
    if (typeof Q === "string")
      return this.__string(J);
    return this.__union(Q, J);
  }
  __indirect(Q) {
    return Q + this.readInt32(Q);
  }
  __vector(Q) {
    return Q + this.readInt32(Q) + YZ;
  }
  __vector_len(Q) {
    return this.readInt32(Q + this.readInt32(Q));
  }
  __has_identifier(Q) {
    if (Q.length != kZ)
      throw new Error("FlatBuffers: file identifier must be length " + kZ);
    for (let J = 0;J < kZ; J++)
      if (Q.charCodeAt(J) != this.readInt8(this.position() + YZ + J))
        return !1;
    return !0;
  }
  createLong(Q, J) {
    return L8.create(Q, J);
  }
  createScalarList(Q, J) {
    let Y = [];
    for (let W = 0;W < J; ++W)
      if (Q(W) !== null)
        Y.push(Q(W));
    return Y;
  }
  createObjList(Q, J) {
    let Y = [];
    for (let W = 0;W < J; ++W) {
      let K = Q(W);
      if (K !== null)
        Y.push(K.unpack());
    }
    return Y;
  }
}

// node_modules/flatbuffers/mjs/builder.js
class V$ {
  constructor(Q) {
    this.minalign = 1, this.vtable = null, this.vtable_in_use = 0, this.isNested = !1, this.object_start = 0, this.vtables = [], this.vector_num_elems = 0, this.force_defaults = !1, this.string_maps = null;
    let J;
    if (!Q)
      J = 1024;
    else
      J = Q;
    this.bb = qZ.allocate(J), this.space = J;
  }
  clear() {
    this.bb.clear(), this.space = this.bb.capacity(), this.minalign = 1, this.vtable = null, this.vtable_in_use = 0, this.isNested = !1, this.object_start = 0, this.vtables = [], this.vector_num_elems = 0, this.force_defaults = !1, this.string_maps = null;
  }
  forceDefaults(Q) {
    this.force_defaults = Q;
  }
  dataBuffer() {
    return this.bb;
  }
  asUint8Array() {
    return this.bb.bytes().subarray(this.bb.position(), this.bb.position() + this.offset());
  }
  prep(Q, J) {
    if (Q > this.minalign)
      this.minalign = Q;
    let Y = ~(this.bb.capacity() - this.space + J) + 1 & Q - 1;
    while (this.space < Y + Q + J) {
      let W = this.bb.capacity();
      this.bb = V$.growByteBuffer(this.bb), this.space += this.bb.capacity() - W;
    }
    this.pad(Y);
  }
  pad(Q) {
    for (let J = 0;J < Q; J++)
      this.bb.writeInt8(--this.space, 0);
  }
  writeInt8(Q) {
    this.bb.writeInt8(this.space -= 1, Q);
  }
  writeInt16(Q) {
    this.bb.writeInt16(this.space -= 2, Q);
  }
  writeInt32(Q) {
    this.bb.writeInt32(this.space -= 4, Q);
  }
  writeInt64(Q) {
    this.bb.writeInt64(this.space -= 8, Q);
  }
  writeFloat32(Q) {
    this.bb.writeFloat32(this.space -= 4, Q);
  }
  writeFloat64(Q) {
    this.bb.writeFloat64(this.space -= 8, Q);
  }
  addInt8(Q) {
    this.prep(1, 0), this.writeInt8(Q);
  }
  addInt16(Q) {
    this.prep(2, 0), this.writeInt16(Q);
  }
  addInt32(Q) {
    this.prep(4, 0), this.writeInt32(Q);
  }
  addInt64(Q) {
    this.prep(8, 0), this.writeInt64(Q);
  }
  addFloat32(Q) {
    this.prep(4, 0), this.writeFloat32(Q);
  }
  addFloat64(Q) {
    this.prep(8, 0), this.writeFloat64(Q);
  }
  addFieldInt8(Q, J, Y) {
    if (this.force_defaults || J != Y)
      this.addInt8(J), this.slot(Q);
  }
  addFieldInt16(Q, J, Y) {
    if (this.force_defaults || J != Y)
      this.addInt16(J), this.slot(Q);
  }
  addFieldInt32(Q, J, Y) {
    if (this.force_defaults || J != Y)
      this.addInt32(J), this.slot(Q);
  }
  addFieldInt64(Q, J, Y) {
    if (this.force_defaults || !J.equals(Y))
      this.addInt64(J), this.slot(Q);
  }
  addFieldFloat32(Q, J, Y) {
    if (this.force_defaults || J != Y)
      this.addFloat32(J), this.slot(Q);
  }
  addFieldFloat64(Q, J, Y) {
    if (this.force_defaults || J != Y)
      this.addFloat64(J), this.slot(Q);
  }
  addFieldOffset(Q, J, Y) {
    if (this.force_defaults || J != Y)
      this.addOffset(J), this.slot(Q);
  }
  addFieldStruct(Q, J, Y) {
    if (J != Y)
      this.nested(J), this.slot(Q);
  }
  nested(Q) {
    if (Q != this.offset())
      throw new Error("FlatBuffers: struct must be serialized inline.");
  }
  notNested() {
    if (this.isNested)
      throw new Error("FlatBuffers: object serialization must not be nested.");
  }
  slot(Q) {
    if (this.vtable !== null)
      this.vtable[Q] = this.offset();
  }
  offset() {
    return this.bb.capacity() - this.space;
  }
  static growByteBuffer(Q) {
    let J = Q.capacity();
    if (J & 3221225472)
      throw new Error("FlatBuffers: cannot grow buffer beyond 2 gigabytes.");
    let Y = J << 1, W = qZ.allocate(Y);
    return W.setPosition(Y - J), W.bytes().set(Q.bytes(), Y - J), W;
  }
  addOffset(Q) {
    this.prep(YZ, 0), this.writeInt32(this.offset() - Q + YZ);
  }
  startObject(Q) {
    if (this.notNested(), this.vtable == null)
      this.vtable = [];
    this.vtable_in_use = Q;
    for (let J = 0;J < Q; J++)
      this.vtable[J] = 0;
    this.isNested = !0, this.object_start = this.offset();
  }
  endObject() {
    if (this.vtable == null || !this.isNested)
      throw new Error("FlatBuffers: endObject called without startObject");
    this.addInt32(0);
    let Q = this.offset(), J = this.vtable_in_use - 1;
    for (;J >= 0 && this.vtable[J] == 0; J--)
      ;
    let Y = J + 1;
    for (;J >= 0; J--)
      this.addInt16(this.vtable[J] != 0 ? Q - this.vtable[J] : 0);
    let W = 2;
    this.addInt16(Q - this.object_start);
    let K = (Y + W) * _3;
    this.addInt16(K);
    let z = 0, N = this.space;
    Q:
      for (J = 0;J < this.vtables.length; J++) {
        let F = this.bb.capacity() - this.vtables[J];
        if (K == this.bb.readInt16(F)) {
          for (let L = _3;L < K; L += _3)
            if (this.bb.readInt16(N + L) != this.bb.readInt16(F + L))
              continue Q;
          z = this.vtables[J];
          break;
        }
      }
    if (z)
      this.space = this.bb.capacity() - Q, this.bb.writeInt32(this.space, z - Q);
    else
      this.vtables.push(this.offset()), this.bb.writeInt32(this.bb.capacity() - Q, this.offset() - Q);
    return this.isNested = !1, Q;
  }
  finish(Q, J, Y) {
    let W = Y ? R0 : 0;
    if (J) {
      let K = J;
      if (this.prep(this.minalign, YZ + kZ + W), K.length != kZ)
        throw new Error("FlatBuffers: file identifier must be length " + kZ);
      for (let z = kZ - 1;z >= 0; z--)
        this.writeInt8(K.charCodeAt(z));
    }
    if (this.prep(this.minalign, YZ + W), this.addOffset(Q), W)
      this.addInt32(this.bb.capacity() - this.space);
    this.bb.setPosition(this.space);
  }
  finishSizePrefixed(Q, J) {
    this.finish(Q, J, !0);
  }
  requiredField(Q, J) {
    let Y = this.bb.capacity() - Q, W = Y - this.bb.readInt32(Y);
    if (this.bb.readInt16(W + J) == 0)
      throw new Error("FlatBuffers: field " + J + " must be set");
  }
  startVector(Q, J, Y) {
    this.notNested(), this.vector_num_elems = J, this.prep(YZ, Q * J), this.prep(Y, Q * J);
  }
  endVector() {
    return this.writeInt32(this.vector_num_elems), this.offset();
  }
  createSharedString(Q) {
    if (!Q)
      return 0;
    if (!this.string_maps)
      this.string_maps = /* @__PURE__ */ new Map;
    if (this.string_maps.has(Q))
      return this.string_maps.get(Q);
    let J = this.createString(Q);
    return this.string_maps.set(Q, J), J;
  }
  createString(Q) {
    if (!Q)
      return 0;
    let J;
    if (Q instanceof Uint8Array)
      J = Q;
    else {
      J = [];
      let Y = 0;
      while (Y < Q.length) {
        let W, K = Q.charCodeAt(Y++);
        if (K < 55296 || K >= 56320)
          W = K;
        else {
          let z = Q.charCodeAt(Y++);
          W = (K << 10) + z + -56613888;
        }
        if (W < 128)
          J.push(W);
        else {
          if (W < 2048)
            J.push(W >> 6 & 31 | 192);
          else {
            if (W < 65536)
              J.push(W >> 12 & 15 | 224);
            else
              J.push(W >> 18 & 7 | 240, W >> 12 & 63 | 128);
            J.push(W >> 6 & 63 | 128);
          }
          J.push(W & 63 | 128);
        }
      }
    }
    this.addInt8(0), this.startVector(1, J.length, 1), this.bb.setPosition(this.space -= J.length);
    for (let Y = 0, W = this.space, K = this.bb.bytes();Y < J.length; Y++)
      K[W++] = J[Y];
    return this.endVector();
  }
  createLong(Q, J) {
    return L8.create(Q, J);
  }
  createObjectOffset(Q) {
    if (Q === null)
      return 0;
    if (typeof Q === "string")
      return this.createString(Q);
    else
      return Q.pack(this);
  }
  createObjectOffsetList(Q) {
    let J = [];
    for (let Y = 0;Y < Q.length; ++Y) {
      let W = Q[Y];
      if (W !== null)
        J.push(this.createObjectOffset(W));
      else
        throw new Error("FlatBuffers: Argument for createObjectOffsetList cannot contain null.");
    }
    return J;
  }
  createStructOffsetList(Q, J) {
    return J(this, Q.length), this.createObjectOffsetList(Q), this.endVector();
  }
}
// node_modules/apache-arrow/fb/key-value.mjs
class P6 {
  constructor() {
    this.bb = null, this.bb_pos = 0;
  }
  __init(Q, J) {
    return this.bb_pos = Q, this.bb = J, this;
  }
  static getRootAsKeyValue(Q, J) {
    return (J || new P6).__init(Q.readInt32(Q.position()) + Q.position(), Q);
  }
  static getSizePrefixedRootAsKeyValue(Q, J) {
    return Q.setPosition(Q.position() + R0), (J || new P6).__init(Q.readInt32(Q.position()) + Q.position(), Q);
  }
  key(Q) {
    let J = this.bb.__offset(this.bb_pos, 4);
    return J ? this.bb.__string(this.bb_pos + J, Q) : null;
  }
  value(Q) {
    let J = this.bb.__offset(this.bb_pos, 6);
    return J ? this.bb.__string(this.bb_pos + J, Q) : null;
  }
  static startKeyValue(Q) {
    Q.startObject(2);
  }
  static addKey(Q, J) {
    Q.addFieldOffset(0, J, 0);
  }
  static addValue(Q, J) {
    Q.addFieldOffset(1, J, 0);
  }
  static endKeyValue(Q) {
    return Q.endObject();
  }
  static createKeyValue(Q, J, Y) {
    return P6.startKeyValue(Q), P6.addKey(Q, J), P6.addValue(Q, Y), P6.endKeyValue(Q);
  }
}

// node_modules/apache-arrow/fb/metadata-version.mjs
var MJ;
(function(Q) {
  Q[Q.V1 = 0] = "V1", Q[Q.V2 = 1] = "V2", Q[Q.V3 = 2] = "V3", Q[Q.V4 = 3] = "V4", Q[Q.V5 = 4] = "V5";
})(MJ || (MJ = {}));

// node_modules/apache-arrow/fb/endianness.mjs
var DJ;
(function(Q) {
  Q[Q.Little = 0] = "Little", Q[Q.Big = 1] = "Big";
})(DJ || (DJ = {}));

// node_modules/apache-arrow/fb/dictionary-kind.mjs
var g3;
(function(Q) {
  Q[Q.DenseArray = 0] = "DenseArray";
})(g3 || (g3 = {}));

// node_modules/apache-arrow/fb/int.mjs
class QQ {
  constructor() {
    this.bb = null, this.bb_pos = 0;
  }
  __init(Q, J) {
    return this.bb_pos = Q, this.bb = J, this;
  }
  static getRootAsInt(Q, J) {
    return (J || new QQ).__init(Q.readInt32(Q.position()) + Q.position(), Q);
  }
  static getSizePrefixedRootAsInt(Q, J) {
    return Q.setPosition(Q.position() + R0), (J || new QQ).__init(Q.readInt32(Q.position()) + Q.position(), Q);
  }
  bitWidth() {
    let Q = this.bb.__offset(this.bb_pos, 4);
    return Q ? this.bb.readInt32(this.bb_pos + Q) : 0;
  }
  isSigned() {
    let Q = this.bb.__offset(this.bb_pos, 6);
    return Q ? !!this.bb.readInt8(this.bb_pos + Q) : !1;
  }
  static startInt(Q) {
    Q.startObject(2);
  }
  static addBitWidth(Q, J) {
    Q.addFieldInt32(0, J, 0);
  }
  static addIsSigned(Q, J) {
    Q.addFieldInt8(1, +J, 0);
  }
  static endInt(Q) {
    return Q.endObject();
  }
  static createInt(Q, J, Y) {
    return QQ.startInt(Q), QQ.addBitWidth(Q, J), QQ.addIsSigned(Q, Y), QQ.endInt(Q);
  }
}

// node_modules/apache-arrow/fb/dictionary-encoding.mjs
class WX {
  constructor() {
    this.bb = null, this.bb_pos = 0;
  }
  __init(Q, J) {
    return this.bb_pos = Q, this.bb = J, this;
  }
  static getRootAsDictionaryEncoding(Q, J) {
    return (J || new WX).__init(Q.readInt32(Q.position()) + Q.position(), Q);
  }
  static getSizePrefixedRootAsDictionaryEncoding(Q, J) {
    return Q.setPosition(Q.position() + R0), (J || new WX).__init(Q.readInt32(Q.position()) + Q.position(), Q);
  }
  id() {
    let Q = this.bb.__offset(this.bb_pos, 4);
    return Q ? this.bb.readInt64(this.bb_pos + Q) : this.bb.createLong(0, 0);
  }
  indexType(Q) {
    let J = this.bb.__offset(this.bb_pos, 6);
    return J ? (Q || new QQ).__init(this.bb.__indirect(this.bb_pos + J), this.bb) : null;
  }
  isOrdered() {
    let Q = this.bb.__offset(this.bb_pos, 8);
    return Q ? !!this.bb.readInt8(this.bb_pos + Q) : !1;
  }
  dictionaryKind() {
    let Q = this.bb.__offset(this.bb_pos, 10);
    return Q ? this.bb.readInt16(this.bb_pos + Q) : g3.DenseArray;
  }
  static startDictionaryEncoding(Q) {
    Q.startObject(4);
  }
  static addId(Q, J) {
    Q.addFieldInt64(0, J, Q.createLong(0, 0));
  }
  static addIndexType(Q, J) {
    Q.addFieldOffset(1, J, 0);
  }
  static addIsOrdered(Q, J) {
    Q.addFieldInt8(2, +J, 0);
  }
  static addDictionaryKind(Q, J) {
    Q.addFieldInt16(3, J, g3.DenseArray);
  }
  static endDictionaryEncoding(Q) {
    return Q.endObject();
  }
}

// node_modules/apache-arrow/fb/binary.mjs
class kJ {
  constructor() {
    this.bb = null, this.bb_pos = 0;
  }
  __init(Q, J) {
    return this.bb_pos = Q, this.bb = J, this;
  }
  static getRootAsBinary(Q, J) {
    return (J || new kJ).__init(Q.readInt32(Q.position()) + Q.position(), Q);
  }
  static getSizePrefixedRootAsBinary(Q, J) {
    return Q.setPosition(Q.position() + R0), (J || new kJ).__init(Q.readInt32(Q.position()) + Q.position(), Q);
  }
  static startBinary(Q) {
    Q.startObject(0);
  }
  static endBinary(Q) {
    return Q.endObject();
  }
  static createBinary(Q) {
    return kJ.startBinary(Q), kJ.endBinary(Q);
  }
}

// node_modules/apache-arrow/fb/bool.mjs
class RJ {
  constructor() {
    this.bb = null, this.bb_pos = 0;
  }
  __init(Q, J) {
    return this.bb_pos = Q, this.bb = J, this;
  }
  static getRootAsBool(Q, J) {
    return (J || new RJ).__init(Q.readInt32(Q.position()) + Q.position(), Q);
  }
  static getSizePrefixedRootAsBool(Q, J) {
    return Q.setPosition(Q.position() + R0), (J || new RJ).__init(Q.readInt32(Q.position()) + Q.position(), Q);
  }
  static startBool(Q) {
    Q.startObject(0);
  }
  static endBool(Q) {
    return Q.endObject();
  }
  static createBool(Q) {
    return RJ.startBool(Q), RJ.endBool(Q);
  }
}

// node_modules/apache-arrow/fb/date-unit.mjs
var x3;
(function(Q) {
  Q[Q.DAY = 0] = "DAY", Q[Q.MILLISECOND = 1] = "MILLISECOND";
})(x3 || (x3 = {}));

// node_modules/apache-arrow/fb/date.mjs
class RZ {
  constructor() {
    this.bb = null, this.bb_pos = 0;
  }
  __init(Q, J) {
    return this.bb_pos = Q, this.bb = J, this;
  }
  static getRootAsDate(Q, J) {
    return (J || new RZ).__init(Q.readInt32(Q.position()) + Q.position(), Q);
  }
  static getSizePrefixedRootAsDate(Q, J) {
    return Q.setPosition(Q.position() + R0), (J || new RZ).__init(Q.readInt32(Q.position()) + Q.position(), Q);
  }
  unit() {
    let Q = this.bb.__offset(this.bb_pos, 4);
    return Q ? this.bb.readInt16(this.bb_pos + Q) : x3.MILLISECOND;
  }
  static startDate(Q) {
    Q.startObject(1);
  }
  static addUnit(Q, J) {
    Q.addFieldInt16(0, J, x3.MILLISECOND);
  }
  static endDate(Q) {
    return Q.endObject();
  }
  static createDate(Q, J) {
    return RZ.startDate(Q), RZ.addUnit(Q, J), RZ.endDate(Q);
  }
}

// node_modules/apache-arrow/fb/decimal.mjs
class ZQ {
  constructor() {
    this.bb = null, this.bb_pos = 0;
  }
  __init(Q, J) {
    return this.bb_pos = Q, this.bb = J, this;
  }
  static getRootAsDecimal(Q, J) {
    return (J || new ZQ).__init(Q.readInt32(Q.position()) + Q.position(), Q);
  }
  static getSizePrefixedRootAsDecimal(Q, J) {
    return Q.setPosition(Q.position() + R0), (J || new ZQ).__init(Q.readInt32(Q.position()) + Q.position(), Q);
  }
  precision() {
    let Q = this.bb.__offset(this.bb_pos, 4);
    return Q ? this.bb.readInt32(this.bb_pos + Q) : 0;
  }
  scale() {
    let Q = this.bb.__offset(this.bb_pos, 6);
    return Q ? this.bb.readInt32(this.bb_pos + Q) : 0;
  }
  bitWidth() {
    let Q = this.bb.__offset(this.bb_pos, 8);
    return Q ? this.bb.readInt32(this.bb_pos + Q) : 128;
  }
  static startDecimal(Q) {
    Q.startObject(3);
  }
  static addPrecision(Q, J) {
    Q.addFieldInt32(0, J, 0);
  }
  static addScale(Q, J) {
    Q.addFieldInt32(1, J, 0);
  }
  static addBitWidth(Q, J) {
    Q.addFieldInt32(2, J, 128);
  }
  static endDecimal(Q) {
    return Q.endObject();
  }
  static createDecimal(Q, J, Y, W) {
    return ZQ.startDecimal(Q), ZQ.addPrecision(Q, J), ZQ.addScale(Q, Y), ZQ.addBitWidth(Q, W), ZQ.endDecimal(Q);
  }
}

// node_modules/apache-arrow/fb/time-unit.mjs
var jJ;
(function(Q) {
  Q[Q.SECOND = 0] = "SECOND", Q[Q.MILLISECOND = 1] = "MILLISECOND", Q[Q.MICROSECOND = 2] = "MICROSECOND", Q[Q.NANOSECOND = 3] = "NANOSECOND";
})(jJ || (jJ = {}));

// node_modules/apache-arrow/fb/fixed-size-binary.mjs
class jZ {
  constructor() {
    this.bb = null, this.bb_pos = 0;
  }
  __init(Q, J) {
    return this.bb_pos = Q, this.bb = J, this;
  }
  static getRootAsFixedSizeBinary(Q, J) {
    return (J || new jZ).__init(Q.readInt32(Q.position()) + Q.position(), Q);
  }
  static getSizePrefixedRootAsFixedSizeBinary(Q, J) {
    return Q.setPosition(Q.position() + R0), (J || new jZ).__init(Q.readInt32(Q.position()) + Q.position(), Q);
  }
  byteWidth() {
    let Q = this.bb.__offset(this.bb_pos, 4);
    return Q ? this.bb.readInt32(this.bb_pos + Q) : 0;
  }
  static startFixedSizeBinary(Q) {
    Q.startObject(1);
  }
  static addByteWidth(Q, J) {
    Q.addFieldInt32(0, J, 0);
  }
  static endFixedSizeBinary(Q) {
    return Q.endObject();
  }
  static createFixedSizeBinary(Q, J) {
    return jZ.startFixedSizeBinary(Q), jZ.addByteWidth(Q, J), jZ.endFixedSizeBinary(Q);
  }
}

// node_modules/apache-arrow/fb/fixed-size-list.mjs
class BZ {
  constructor() {
    this.bb = null, this.bb_pos = 0;
  }
  __init(Q, J) {
    return this.bb_pos = Q, this.bb = J, this;
  }
  static getRootAsFixedSizeList(Q, J) {
    return (J || new BZ).__init(Q.readInt32(Q.position()) + Q.position(), Q);
  }
  static getSizePrefixedRootAsFixedSizeList(Q, J) {
    return Q.setPosition(Q.position() + R0), (J || new BZ).__init(Q.readInt32(Q.position()) + Q.position(), Q);
  }
  listSize() {
    let Q = this.bb.__offset(this.bb_pos, 4);
    return Q ? this.bb.readInt32(this.bb_pos + Q) : 0;
  }
  static startFixedSizeList(Q) {
    Q.startObject(1);
  }
  static addListSize(Q, J) {
    Q.addFieldInt32(0, J, 0);
  }
  static endFixedSizeList(Q) {
    return Q.endObject();
  }
  static createFixedSizeList(Q, J) {
    return BZ.startFixedSizeList(Q), BZ.addListSize(Q, J), BZ.endFixedSizeList(Q);
  }
}

// node_modules/apache-arrow/fb/precision.mjs
var v3;
(function(Q) {
  Q[Q.HALF = 0] = "HALF", Q[Q.SINGLE = 1] = "SINGLE", Q[Q.DOUBLE = 2] = "DOUBLE";
})(v3 || (v3 = {}));

// node_modules/apache-arrow/fb/floating-point.mjs
class CZ {
  constructor() {
    this.bb = null, this.bb_pos = 0;
  }
  __init(Q, J) {
    return this.bb_pos = Q, this.bb = J, this;
  }
  static getRootAsFloatingPoint(Q, J) {
    return (J || new CZ).__init(Q.readInt32(Q.position()) + Q.position(), Q);
  }
  static getSizePrefixedRootAsFloatingPoint(Q, J) {
    return Q.setPosition(Q.position() + R0), (J || new CZ).__init(Q.readInt32(Q.position()) + Q.position(), Q);
  }
  precision() {
    let Q = this.bb.__offset(this.bb_pos, 4);
    return Q ? this.bb.readInt16(this.bb_pos + Q) : v3.HALF;
  }
  static startFloatingPoint(Q) {
    Q.startObject(1);
  }
  static addPrecision(Q, J) {
    Q.addFieldInt16(0, J, v3.HALF);
  }
  static endFloatingPoint(Q) {
    return Q.endObject();
  }
  static createFloatingPoint(Q, J) {
    return CZ.startFloatingPoint(Q), CZ.addPrecision(Q, J), CZ.endFloatingPoint(Q);
  }
}

// node_modules/apache-arrow/fb/interval-unit.mjs
var h3;
(function(Q) {
  Q[Q.YEAR_MONTH = 0] = "YEAR_MONTH", Q[Q.DAY_TIME = 1] = "DAY_TIME", Q[Q.MONTH_DAY_NANO = 2] = "MONTH_DAY_NANO";
})(h3 || (h3 = {}));

// node_modules/apache-arrow/fb/interval.mjs
class VZ {
  constructor() {
    this.bb = null, this.bb_pos = 0;
  }
  __init(Q, J) {
    return this.bb_pos = Q, this.bb = J, this;
  }
  static getRootAsInterval(Q, J) {
    return (J || new VZ).__init(Q.readInt32(Q.position()) + Q.position(), Q);
  }
  static getSizePrefixedRootAsInterval(Q, J) {
    return Q.setPosition(Q.position() + R0), (J || new VZ).__init(Q.readInt32(Q.position()) + Q.position(), Q);
  }
  unit() {
    let Q = this.bb.__offset(this.bb_pos, 4);
    return Q ? this.bb.readInt16(this.bb_pos + Q) : h3.YEAR_MONTH;
  }
  static startInterval(Q) {
    Q.startObject(1);
  }
  static addUnit(Q, J) {
    Q.addFieldInt16(0, J, h3.YEAR_MONTH);
  }
  static endInterval(Q) {
    return Q.endObject();
  }
  static createInterval(Q, J) {
    return VZ.startInterval(Q), VZ.addUnit(Q, J), VZ.endInterval(Q);
  }
}

// node_modules/apache-arrow/fb/list.mjs
class BJ {
  constructor() {
    this.bb = null, this.bb_pos = 0;
  }
  __init(Q, J) {
    return this.bb_pos = Q, this.bb = J, this;
  }
  static getRootAsList(Q, J) {
    return (J || new BJ).__init(Q.readInt32(Q.position()) + Q.position(), Q);
  }
  static getSizePrefixedRootAsList(Q, J) {
    return Q.setPosition(Q.position() + R0), (J || new BJ).__init(Q.readInt32(Q.position()) + Q.position(), Q);
  }
  static startList(Q) {
    Q.startObject(0);
  }
  static endList(Q) {
    return Q.endObject();
  }
  static createList(Q) {
    return BJ.startList(Q), BJ.endList(Q);
  }
}

// node_modules/apache-arrow/fb/map.mjs
class SZ {
  constructor() {
    this.bb = null, this.bb_pos = 0;
  }
  __init(Q, J) {
    return this.bb_pos = Q, this.bb = J, this;
  }
  static getRootAsMap(Q, J) {
    return (J || new SZ).__init(Q.readInt32(Q.position()) + Q.position(), Q);
  }
  static getSizePrefixedRootAsMap(Q, J) {
    return Q.setPosition(Q.position() + R0), (J || new SZ).__init(Q.readInt32(Q.position()) + Q.position(), Q);
  }
  keysSorted() {
    let Q = this.bb.__offset(this.bb_pos, 4);
    return Q ? !!this.bb.readInt8(this.bb_pos + Q) : !1;
  }
  static startMap(Q) {
    Q.startObject(1);
  }
  static addKeysSorted(Q, J) {
    Q.addFieldInt8(0, +J, 0);
  }
  static endMap(Q) {
    return Q.endObject();
  }
  static createMap(Q, J) {
    return SZ.startMap(Q), SZ.addKeysSorted(Q, J), SZ.endMap(Q);
  }
}

// node_modules/apache-arrow/fb/null.mjs
class CJ {
  constructor() {
    this.bb = null, this.bb_pos = 0;
  }
  __init(Q, J) {
    return this.bb_pos = Q, this.bb = J, this;
  }
  static getRootAsNull(Q, J) {
    return (J || new CJ).__init(Q.readInt32(Q.position()) + Q.position(), Q);
  }
  static getSizePrefixedRootAsNull(Q, J) {
    return Q.setPosition(Q.position() + R0), (J || new CJ).__init(Q.readInt32(Q.position()) + Q.position(), Q);
  }
  static startNull(Q) {
    Q.startObject(0);
  }
  static endNull(Q) {
    return Q.endObject();
  }
  static createNull(Q) {
    return CJ.startNull(Q), CJ.endNull(Q);
  }
}

// node_modules/apache-arrow/fb/struct_.mjs
class VJ {
  constructor() {
    this.bb = null, this.bb_pos = 0;
  }
  __init(Q, J) {
    return this.bb_pos = Q, this.bb = J, this;
  }
  static getRootAsStruct_(Q, J) {
    return (J || new VJ).__init(Q.readInt32(Q.position()) + Q.position(), Q);
  }
  static getSizePrefixedRootAsStruct_(Q, J) {
    return Q.setPosition(Q.position() + R0), (J || new VJ).__init(Q.readInt32(Q.position()) + Q.position(), Q);
  }
  static startStruct_(Q) {
    Q.startObject(0);
  }
  static endStruct_(Q) {
    return Q.endObject();
  }
  static createStruct_(Q) {
    return VJ.startStruct_(Q), VJ.endStruct_(Q);
  }
}

// node_modules/apache-arrow/fb/time.mjs
class hQ {
  constructor() {
    this.bb = null, this.bb_pos = 0;
  }
  __init(Q, J) {
    return this.bb_pos = Q, this.bb = J, this;
  }
  static getRootAsTime(Q, J) {
    return (J || new hQ).__init(Q.readInt32(Q.position()) + Q.position(), Q);
  }
  static getSizePrefixedRootAsTime(Q, J) {
    return Q.setPosition(Q.position() + R0), (J || new hQ).__init(Q.readInt32(Q.position()) + Q.position(), Q);
  }
  unit() {
    let Q = this.bb.__offset(this.bb_pos, 4);
    return Q ? this.bb.readInt16(this.bb_pos + Q) : jJ.MILLISECOND;
  }
  bitWidth() {
    let Q = this.bb.__offset(this.bb_pos, 6);
    return Q ? this.bb.readInt32(this.bb_pos + Q) : 32;
  }
  static startTime(Q) {
    Q.startObject(2);
  }
  static addUnit(Q, J) {
    Q.addFieldInt16(0, J, jJ.MILLISECOND);
  }
  static addBitWidth(Q, J) {
    Q.addFieldInt32(1, J, 32);
  }
  static endTime(Q) {
    return Q.endObject();
  }
  static createTime(Q, J, Y) {
    return hQ.startTime(Q), hQ.addUnit(Q, J), hQ.addBitWidth(Q, Y), hQ.endTime(Q);
  }
}

// node_modules/apache-arrow/fb/timestamp.mjs
class yQ {
  constructor() {
    this.bb = null, this.bb_pos = 0;
  }
  __init(Q, J) {
    return this.bb_pos = Q, this.bb = J, this;
  }
  static getRootAsTimestamp(Q, J) {
    return (J || new yQ).__init(Q.readInt32(Q.position()) + Q.position(), Q);
  }
  static getSizePrefixedRootAsTimestamp(Q, J) {
    return Q.setPosition(Q.position() + R0), (J || new yQ).__init(Q.readInt32(Q.position()) + Q.position(), Q);
  }
  unit() {
    let Q = this.bb.__offset(this.bb_pos, 4);
    return Q ? this.bb.readInt16(this.bb_pos + Q) : jJ.SECOND;
  }
  timezone(Q) {
    let J = this.bb.__offset(this.bb_pos, 6);
    return J ? this.bb.__string(this.bb_pos + J, Q) : null;
  }
  static startTimestamp(Q) {
    Q.startObject(2);
  }
  static addUnit(Q, J) {
    Q.addFieldInt16(0, J, jJ.SECOND);
  }
  static addTimezone(Q, J) {
    Q.addFieldOffset(1, J, 0);
  }
  static endTimestamp(Q) {
    return Q.endObject();
  }
  static createTimestamp(Q, J, Y) {
    return yQ.startTimestamp(Q), yQ.addUnit(Q, J), yQ.addTimezone(Q, Y), yQ.endTimestamp(Q);
  }
}

// node_modules/apache-arrow/fb/union-mode.mjs
var y3;
(function(Q) {
  Q[Q.Sparse = 0] = "Sparse", Q[Q.Dense = 1] = "Dense";
})(y3 || (y3 = {}));

// node_modules/apache-arrow/fb/union.mjs
class XQ {
  constructor() {
    this.bb = null, this.bb_pos = 0;
  }
  __init(Q, J) {
    return this.bb_pos = Q, this.bb = J, this;
  }
  static getRootAsUnion(Q, J) {
    return (J || new XQ).__init(Q.readInt32(Q.position()) + Q.position(), Q);
  }
  static getSizePrefixedRootAsUnion(Q, J) {
    return Q.setPosition(Q.position() + R0), (J || new XQ).__init(Q.readInt32(Q.position()) + Q.position(), Q);
  }
  mode() {
    let Q = this.bb.__offset(this.bb_pos, 4);
    return Q ? this.bb.readInt16(this.bb_pos + Q) : y3.Sparse;
  }
  typeIds(Q) {
    let J = this.bb.__offset(this.bb_pos, 6);
    return J ? this.bb.readInt32(this.bb.__vector(this.bb_pos + J) + Q * 4) : 0;
  }
  typeIdsLength() {
    let Q = this.bb.__offset(this.bb_pos, 6);
    return Q ? this.bb.__vector_len(this.bb_pos + Q) : 0;
  }
  typeIdsArray() {
    let Q = this.bb.__offset(this.bb_pos, 6);
    return Q ? new Int32Array(this.bb.bytes().buffer, this.bb.bytes().byteOffset + this.bb.__vector(this.bb_pos + Q), this.bb.__vector_len(this.bb_pos + Q)) : null;
  }
  static startUnion(Q) {
    Q.startObject(2);
  }
  static addMode(Q, J) {
    Q.addFieldInt16(0, J, y3.Sparse);
  }
  static addTypeIds(Q, J) {
    Q.addFieldOffset(1, J, 0);
  }
  static createTypeIdsVector(Q, J) {
    Q.startVector(4, J.length, 4);
    for (let Y = J.length - 1;Y >= 0; Y--)
      Q.addInt32(J[Y]);
    return Q.endVector();
  }
  static startTypeIdsVector(Q, J) {
    Q.startVector(4, J, 4);
  }
  static endUnion(Q) {
    return Q.endObject();
  }
  static createUnion(Q, J, Y) {
    return XQ.startUnion(Q), XQ.addMode(Q, J), XQ.addTypeIds(Q, Y), XQ.endUnion(Q);
  }
}

// node_modules/apache-arrow/fb/utf8.mjs
class SJ {
  constructor() {
    this.bb = null, this.bb_pos = 0;
  }
  __init(Q, J) {
    return this.bb_pos = Q, this.bb = J, this;
  }
  static getRootAsUtf8(Q, J) {
    return (J || new SJ).__init(Q.readInt32(Q.position()) + Q.position(), Q);
  }
  static getSizePrefixedRootAsUtf8(Q, J) {
    return Q.setPosition(Q.position() + R0), (J || new SJ).__init(Q.readInt32(Q.position()) + Q.position(), Q);
  }
  static startUtf8(Q) {
    Q.startObject(0);
  }
  static endUtf8(Q) {
    return Q.endObject();
  }
  static createUtf8(Q) {
    return SJ.startUtf8(Q), SJ.endUtf8(Q);
  }
}

// node_modules/apache-arrow/fb/type.mjs
var G6;
(function(Q) {
  Q[Q.NONE = 0] = "NONE", Q[Q.Null = 1] = "Null", Q[Q.Int = 2] = "Int", Q[Q.FloatingPoint = 3] = "FloatingPoint", Q[Q.Binary = 4] = "Binary", Q[Q.Utf8 = 5] = "Utf8", Q[Q.Bool = 6] = "Bool", Q[Q.Decimal = 7] = "Decimal", Q[Q.Date = 8] = "Date", Q[Q.Time = 9] = "Time", Q[Q.Timestamp = 10] = "Timestamp", Q[Q.Interval = 11] = "Interval", Q[Q.List = 12] = "List", Q[Q.Struct_ = 13] = "Struct_", Q[Q.Union = 14] = "Union", Q[Q.FixedSizeBinary = 15] = "FixedSizeBinary", Q[Q.FixedSizeList = 16] = "FixedSizeList", Q[Q.Map = 17] = "Map", Q[Q.Duration = 18] = "Duration", Q[Q.LargeBinary = 19] = "LargeBinary", Q[Q.LargeUtf8 = 20] = "LargeUtf8", Q[Q.LargeList = 21] = "LargeList";
})(G6 || (G6 = {}));

// node_modules/apache-arrow/fb/field.mjs
class O8 {
  constructor() {
    this.bb = null, this.bb_pos = 0;
  }
  __init(Q, J) {
    return this.bb_pos = Q, this.bb = J, this;
  }
  static getRootAsField(Q, J) {
    return (J || new O8).__init(Q.readInt32(Q.position()) + Q.position(), Q);
  }
  static getSizePrefixedRootAsField(Q, J) {
    return Q.setPosition(Q.position() + R0), (J || new O8).__init(Q.readInt32(Q.position()) + Q.position(), Q);
  }
  name(Q) {
    let J = this.bb.__offset(this.bb_pos, 4);
    return J ? this.bb.__string(this.bb_pos + J, Q) : null;
  }
  nullable() {
    let Q = this.bb.__offset(this.bb_pos, 6);
    return Q ? !!this.bb.readInt8(this.bb_pos + Q) : !1;
  }
  typeType() {
    let Q = this.bb.__offset(this.bb_pos, 8);
    return Q ? this.bb.readUint8(this.bb_pos + Q) : G6.NONE;
  }
  type(Q) {
    let J = this.bb.__offset(this.bb_pos, 10);
    return J ? this.bb.__union(Q, this.bb_pos + J) : null;
  }
  dictionary(Q) {
    let J = this.bb.__offset(this.bb_pos, 12);
    return J ? (Q || new WX).__init(this.bb.__indirect(this.bb_pos + J), this.bb) : null;
  }
  children(Q, J) {
    let Y = this.bb.__offset(this.bb_pos, 14);
    return Y ? (J || new O8).__init(this.bb.__indirect(this.bb.__vector(this.bb_pos + Y) + Q * 4), this.bb) : null;
  }
  childrenLength() {
    let Q = this.bb.__offset(this.bb_pos, 14);
    return Q ? this.bb.__vector_len(this.bb_pos + Q) : 0;
  }
  customMetadata(Q, J) {
    let Y = this.bb.__offset(this.bb_pos, 16);
    return Y ? (J || new P6).__init(this.bb.__indirect(this.bb.__vector(this.bb_pos + Y) + Q * 4), this.bb) : null;
  }
  customMetadataLength() {
    let Q = this.bb.__offset(this.bb_pos, 16);
    return Q ? this.bb.__vector_len(this.bb_pos + Q) : 0;
  }
  static startField(Q) {
    Q.startObject(7);
  }
  static addName(Q, J) {
    Q.addFieldOffset(0, J, 0);
  }
  static addNullable(Q, J) {
    Q.addFieldInt8(1, +J, 0);
  }
  static addTypeType(Q, J) {
    Q.addFieldInt8(2, J, G6.NONE);
  }
  static addType(Q, J) {
    Q.addFieldOffset(3, J, 0);
  }
  static addDictionary(Q, J) {
    Q.addFieldOffset(4, J, 0);
  }
  static addChildren(Q, J) {
    Q.addFieldOffset(5, J, 0);
  }
  static createChildrenVector(Q, J) {
    Q.startVector(4, J.length, 4);
    for (let Y = J.length - 1;Y >= 0; Y--)
      Q.addOffset(J[Y]);
    return Q.endVector();
  }
  static startChildrenVector(Q, J) {
    Q.startVector(4, J, 4);
  }
  static addCustomMetadata(Q, J) {
    Q.addFieldOffset(6, J, 0);
  }
  static createCustomMetadataVector(Q, J) {
    Q.startVector(4, J.length, 4);
    for (let Y = J.length - 1;Y >= 0; Y--)
      Q.addOffset(J[Y]);
    return Q.endVector();
  }
  static startCustomMetadataVector(Q, J) {
    Q.startVector(4, J, 4);
  }
  static endField(Q) {
    return Q.endObject();
  }
}

// node_modules/apache-arrow/fb/schema.mjs
class I6 {
  constructor() {
    this.bb = null, this.bb_pos = 0;
  }
  __init(Q, J) {
    return this.bb_pos = Q, this.bb = J, this;
  }
  static getRootAsSchema(Q, J) {
    return (J || new I6).__init(Q.readInt32(Q.position()) + Q.position(), Q);
  }
  static getSizePrefixedRootAsSchema(Q, J) {
    return Q.setPosition(Q.position() + R0), (J || new I6).__init(Q.readInt32(Q.position()) + Q.position(), Q);
  }
  endianness() {
    let Q = this.bb.__offset(this.bb_pos, 4);
    return Q ? this.bb.readInt16(this.bb_pos + Q) : DJ.Little;
  }
  fields(Q, J) {
    let Y = this.bb.__offset(this.bb_pos, 6);
    return Y ? (J || new O8).__init(this.bb.__indirect(this.bb.__vector(this.bb_pos + Y) + Q * 4), this.bb) : null;
  }
  fieldsLength() {
    let Q = this.bb.__offset(this.bb_pos, 6);
    return Q ? this.bb.__vector_len(this.bb_pos + Q) : 0;
  }
  customMetadata(Q, J) {
    let Y = this.bb.__offset(this.bb_pos, 8);
    return Y ? (J || new P6).__init(this.bb.__indirect(this.bb.__vector(this.bb_pos + Y) + Q * 4), this.bb) : null;
  }
  customMetadataLength() {
    let Q = this.bb.__offset(this.bb_pos, 8);
    return Q ? this.bb.__vector_len(this.bb_pos + Q) : 0;
  }
  features(Q) {
    let J = this.bb.__offset(this.bb_pos, 10);
    return J ? this.bb.readInt64(this.bb.__vector(this.bb_pos + J) + Q * 8) : this.bb.createLong(0, 0);
  }
  featuresLength() {
    let Q = this.bb.__offset(this.bb_pos, 10);
    return Q ? this.bb.__vector_len(this.bb_pos + Q) : 0;
  }
  static startSchema(Q) {
    Q.startObject(4);
  }
  static addEndianness(Q, J) {
    Q.addFieldInt16(0, J, DJ.Little);
  }
  static addFields(Q, J) {
    Q.addFieldOffset(1, J, 0);
  }
  static createFieldsVector(Q, J) {
    Q.startVector(4, J.length, 4);
    for (let Y = J.length - 1;Y >= 0; Y--)
      Q.addOffset(J[Y]);
    return Q.endVector();
  }
  static startFieldsVector(Q, J) {
    Q.startVector(4, J, 4);
  }
  static addCustomMetadata(Q, J) {
    Q.addFieldOffset(2, J, 0);
  }
  static createCustomMetadataVector(Q, J) {
    Q.startVector(4, J.length, 4);
    for (let Y = J.length - 1;Y >= 0; Y--)
      Q.addOffset(J[Y]);
    return Q.endVector();
  }
  static startCustomMetadataVector(Q, J) {
    Q.startVector(4, J, 4);
  }
  static addFeatures(Q, J) {
    Q.addFieldOffset(3, J, 0);
  }
  static createFeaturesVector(Q, J) {
    Q.startVector(8, J.length, 8);
    for (let Y = J.length - 1;Y >= 0; Y--)
      Q.addInt64(J[Y]);
    return Q.endVector();
  }
  static startFeaturesVector(Q, J) {
    Q.startVector(8, J, 8);
  }
  static endSchema(Q) {
    return Q.endObject();
  }
  static finishSchemaBuffer(Q, J) {
    Q.finish(J);
  }
  static finishSizePrefixedSchemaBuffer(Q, J) {
    Q.finish(J, void 0, !0);
  }
  static createSchema(Q, J, Y, W, K) {
    return I6.startSchema(Q), I6.addEndianness(Q, J), I6.addFields(Q, Y), I6.addCustomMetadata(Q, W), I6.addFeatures(Q, K), I6.endSchema(Q);
  }
}

// node_modules/apache-arrow/fb/footer.mjs
class fQ {
  constructor() {
    this.bb = null, this.bb_pos = 0;
  }
  __init(Q, J) {
    return this.bb_pos = Q, this.bb = J, this;
  }
  static getRootAsFooter(Q, J) {
    return (J || new fQ).__init(Q.readInt32(Q.position()) + Q.position(), Q);
  }
  static getSizePrefixedRootAsFooter(Q, J) {
    return Q.setPosition(Q.position() + R0), (J || new fQ).__init(Q.readInt32(Q.position()) + Q.position(), Q);
  }
  version() {
    let Q = this.bb.__offset(this.bb_pos, 4);
    return Q ? this.bb.readInt16(this.bb_pos + Q) : MJ.V1;
  }
  schema(Q) {
    let J = this.bb.__offset(this.bb_pos, 6);
    return J ? (Q || new I6).__init(this.bb.__indirect(this.bb_pos + J), this.bb) : null;
  }
  dictionaries(Q, J) {
    let Y = this.bb.__offset(this.bb_pos, 8);
    return Y ? (J || new Kq).__init(this.bb.__vector(this.bb_pos + Y) + Q * 24, this.bb) : null;
  }
  dictionariesLength() {
    let Q = this.bb.__offset(this.bb_pos, 8);
    return Q ? this.bb.__vector_len(this.bb_pos + Q) : 0;
  }
  recordBatches(Q, J) {
    let Y = this.bb.__offset(this.bb_pos, 10);
    return Y ? (J || new Kq).__init(this.bb.__vector(this.bb_pos + Y) + Q * 24, this.bb) : null;
  }
  recordBatchesLength() {
    let Q = this.bb.__offset(this.bb_pos, 10);
    return Q ? this.bb.__vector_len(this.bb_pos + Q) : 0;
  }
  customMetadata(Q, J) {
    let Y = this.bb.__offset(this.bb_pos, 12);
    return Y ? (J || new P6).__init(this.bb.__indirect(this.bb.__vector(this.bb_pos + Y) + Q * 4), this.bb) : null;
  }
  customMetadataLength() {
    let Q = this.bb.__offset(this.bb_pos, 12);
    return Q ? this.bb.__vector_len(this.bb_pos + Q) : 0;
  }
  static startFooter(Q) {
    Q.startObject(5);
  }
  static addVersion(Q, J) {
    Q.addFieldInt16(0, J, MJ.V1);
  }
  static addSchema(Q, J) {
    Q.addFieldOffset(1, J, 0);
  }
  static addDictionaries(Q, J) {
    Q.addFieldOffset(2, J, 0);
  }
  static startDictionariesVector(Q, J) {
    Q.startVector(24, J, 8);
  }
  static addRecordBatches(Q, J) {
    Q.addFieldOffset(3, J, 0);
  }
  static startRecordBatchesVector(Q, J) {
    Q.startVector(24, J, 8);
  }
  static addCustomMetadata(Q, J) {
    Q.addFieldOffset(4, J, 0);
  }
  static createCustomMetadataVector(Q, J) {
    Q.startVector(4, J.length, 4);
    for (let Y = J.length - 1;Y >= 0; Y--)
      Q.addOffset(J[Y]);
    return Q.endVector();
  }
  static startCustomMetadataVector(Q, J) {
    Q.startVector(4, J, 4);
  }
  static endFooter(Q) {
    return Q.endObject();
  }
  static finishFooterBuffer(Q, J) {
    Q.finish(J);
  }
  static finishSizePrefixedFooterBuffer(Q, J) {
    Q.finish(J, void 0, !0);
  }
}

// node_modules/apache-arrow/schema.mjs
class w1 {
  constructor(Q = [], J, Y) {
    if (this.fields = Q || [], this.metadata = J || /* @__PURE__ */ new Map, !Y)
      Y = QE(Q);
    this.dictionaries = Y;
  }
  get [Symbol.toStringTag]() {
    return "Schema";
  }
  get names() {
    return this.fields.map((Q) => Q.name);
  }
  toString() {
    return `Schema<{ ${this.fields.map((Q, J) => `${J}: ${Q}`).join(", ")} }>`;
  }
  select(Q) {
    let J = new Set(Q), Y = this.fields.filter((W) => J.has(W.name));
    return new w1(Y, this.metadata);
  }
  selectAt(Q) {
    let J = Q.map((Y) => this.fields[Y]).filter(Boolean);
    return new w1(J, this.metadata);
  }
  assign(...Q) {
    let J = Q[0] instanceof w1 ? Q[0] : Array.isArray(Q[0]) ? new w1(Q[0]) : new w1(Q), Y = [...this.fields], W = HH(HH(/* @__PURE__ */ new Map, this.metadata), J.metadata), K = J.fields.filter((N) => {
      let F = Y.findIndex((L) => L.name === N.name);
      return ~F ? (Y[F] = N.clone({
        metadata: HH(HH(/* @__PURE__ */ new Map, Y[F].metadata), N.metadata)
      })) && !1 : !0;
    }), z = QE(K, /* @__PURE__ */ new Map);
    return new w1([...Y, ...K], W, new Map([...this.dictionaries, ...z]));
  }
}
w1.prototype.fields = null;
w1.prototype.metadata = null;
w1.prototype.dictionaries = null;

class q1 {
  constructor(Q, J, Y = !1, W) {
    this.name = Q, this.type = J, this.nullable = Y, this.metadata = W || /* @__PURE__ */ new Map;
  }
  static new(...Q) {
    let [J, Y, W, K] = Q;
    if (Q[0] && typeof Q[0] === "object")
      ({ name: J } = Q[0]), Y === void 0 && (Y = Q[0].type), W === void 0 && (W = Q[0].nullable), K === void 0 && (K = Q[0].metadata);
    return new q1(`${J}`, Y, W, K);
  }
  get typeId() {
    return this.type.typeId;
  }
  get [Symbol.toStringTag]() {
    return "Field";
  }
  toString() {
    return `${this.name}: ${this.type}`;
  }
  clone(...Q) {
    let [J, Y, W, K] = Q;
    return !Q[0] || typeof Q[0] !== "object" ? [J = this.name, Y = this.type, W = this.nullable, K = this.metadata] = Q : { name: J = this.name, type: Y = this.type, nullable: W = this.nullable, metadata: K = this.metadata } = Q[0], q1.new(J, Y, W, K);
  }
}
q1.prototype.type = null;
q1.prototype.name = null;
q1.prototype.nullable = null;
q1.prototype.metadata = null;
function HH(Q, J) {
  return new Map([...Q || /* @__PURE__ */ new Map, ...J || /* @__PURE__ */ new Map]);
}
function QE(Q, J = /* @__PURE__ */ new Map) {
  for (let Y = -1, W = Q.length;++Y < W; ) {
    let z = Q[Y].type;
    if (C0.isDictionary(z)) {
      if (!J.has(z.id))
        J.set(z.id, z.dictionary);
      else if (J.get(z.id) !== z.dictionary)
        throw new Error("Cannot create Schema containing two different dictionaries with the same Id");
    }
    if (z.children && z.children.length > 0)
      QE(z.children, J);
  }
  return J;
}

// node_modules/apache-arrow/ipc/metadata/file.mjs
var WD = L8, Ch = V$, Vh = qZ;

class IJ {
  constructor(Q, J = A8.V4, Y, W) {
    this.schema = Q, this.version = J, Y && (this._recordBatches = Y), W && (this._dictionaryBatches = W);
  }
  static decode(Q) {
    Q = new Vh(n0(Q));
    let J = fQ.getRootAsFooter(Q), Y = w1.decode(J.schema());
    return new KD(Y, J);
  }
  static encode(Q) {
    let J = new Ch, Y = w1.encode(J, Q.schema);
    fQ.startRecordBatchesVector(J, Q.numRecordBatches);
    for (let z of [...Q.recordBatches()].slice().reverse())
      k4.encode(J, z);
    let W = J.endVector();
    fQ.startDictionariesVector(J, Q.numDictionaries);
    for (let z of [...Q.dictionaryBatches()].slice().reverse())
      k4.encode(J, z);
    let K = J.endVector();
    return fQ.startFooter(J), fQ.addSchema(J, Y), fQ.addVersion(J, A8.V4), fQ.addRecordBatches(J, W), fQ.addDictionaries(J, K), fQ.finishFooterBuffer(J, fQ.endFooter(J)), J.asUint8Array();
  }
  get numRecordBatches() {
    return this._recordBatches.length;
  }
  get numDictionaries() {
    return this._dictionaryBatches.length;
  }
  *recordBatches() {
    for (let Q, J = -1, Y = this.numRecordBatches;++J < Y; )
      if (Q = this.getRecordBatch(J))
        yield Q;
  }
  *dictionaryBatches() {
    for (let Q, J = -1, Y = this.numDictionaries;++J < Y; )
      if (Q = this.getDictionaryBatch(J))
        yield Q;
  }
  getRecordBatch(Q) {
    return Q >= 0 && Q < this.numRecordBatches && this._recordBatches[Q] || null;
  }
  getDictionaryBatch(Q) {
    return Q >= 0 && Q < this.numDictionaries && this._dictionaryBatches[Q] || null;
  }
}
class KD extends IJ {
  constructor(Q, J) {
    super(Q, J.version());
    this._footer = J;
  }
  get numRecordBatches() {
    return this._footer.recordBatchesLength();
  }
  get numDictionaries() {
    return this._footer.dictionariesLength();
  }
  getRecordBatch(Q) {
    if (Q >= 0 && Q < this.numRecordBatches) {
      let J = this._footer.recordBatches(Q);
      if (J)
        return k4.decode(J);
    }
    return null;
  }
  getDictionaryBatch(Q) {
    if (Q >= 0 && Q < this.numDictionaries) {
      let J = this._footer.dictionaries(Q);
      if (J)
        return k4.decode(J);
    }
    return null;
  }
}

class k4 {
  constructor(Q, J, Y) {
    this.metaDataLength = Q, this.offset = typeof Y === "number" ? Y : Y.low, this.bodyLength = typeof J === "number" ? J : J.low;
  }
  static decode(Q) {
    return new k4(Q.metaDataLength(), Q.bodyLength(), Q.offset());
  }
  static encode(Q, J) {
    let { metaDataLength: Y } = J, W = new WD(J.offset, 0), K = new WD(J.bodyLength, 0);
    return Kq.createBlock(Q, W, Y, K);
  }
}

// node_modules/apache-arrow/io/interfaces.mjs
var Y6 = Object.freeze({ done: !0, value: void 0 });

class GH {
  constructor(Q) {
    this._json = Q;
  }
  get schema() {
    return this._json.schema;
  }
  get batches() {
    return this._json.batches || [];
  }
  get dictionaries() {
    return this._json.dictionaries || [];
  }
}

class Gq {
  tee() {
    return this._getDOMStream().tee();
  }
  pipe(Q, J) {
    return this._getNodeStream().pipe(Q, J);
  }
  pipeTo(Q, J) {
    return this._getDOMStream().pipeTo(Q, J);
  }
  pipeThrough(Q, J) {
    return this._getDOMStream().pipeThrough(Q, J);
  }
  _getDOMStream() {
    return this._DOMStream || (this._DOMStream = this.toDOMStream());
  }
  _getNodeStream() {
    return this._nodeStream || (this._nodeStream = this.toNodeStream());
  }
}

class ZE extends Gq {
  constructor() {
    super();
    this._values = [], this.resolvers = [], this._closedPromise = new Promise((Q) => this._closedPromiseResolve = Q);
  }
  get closed() {
    return this._closedPromise;
  }
  cancel(Q) {
    return U0(this, void 0, void 0, function* () {
      yield this.return(Q);
    });
  }
  write(Q) {
    if (this._ensureOpen())
      this.resolvers.length <= 0 ? this._values.push(Q) : this.resolvers.shift().resolve({ done: !1, value: Q });
  }
  abort(Q) {
    if (this._closedPromiseResolve)
      this.resolvers.length <= 0 ? this._error = { error: Q } : this.resolvers.shift().reject({ done: !0, value: Q });
  }
  close() {
    if (this._closedPromiseResolve) {
      let { resolvers: Q } = this;
      while (Q.length > 0)
        Q.shift().resolve(Y6);
      this._closedPromiseResolve(), this._closedPromiseResolve = void 0;
    }
  }
  [Symbol.asyncIterator]() {
    return this;
  }
  toDOMStream(Q) {
    return y8.toDOMStream(this._closedPromiseResolve || this._error ? this : this._values, Q);
  }
  toNodeStream(Q) {
    return y8.toNodeStream(this._closedPromiseResolve || this._error ? this : this._values, Q);
  }
  throw(Q) {
    return U0(this, void 0, void 0, function* () {
      return yield this.abort(Q), Y6;
    });
  }
  return(Q) {
    return U0(this, void 0, void 0, function* () {
      return yield this.close(), Y6;
    });
  }
  read(Q) {
    return U0(this, void 0, void 0, function* () {
      return (yield this.next(Q, "read")).value;
    });
  }
  peek(Q) {
    return U0(this, void 0, void 0, function* () {
      return (yield this.next(Q, "peek")).value;
    });
  }
  next(...Q) {
    if (this._values.length > 0)
      return Promise.resolve({ done: !1, value: this._values.shift() });
    else if (this._error)
      return Promise.reject({ done: !0, value: this._error.error });
    else if (!this._closedPromiseResolve)
      return Promise.resolve(Y6);
    else
      return new Promise((J, Y) => {
        this.resolvers.push({ resolve: J, reject: Y });
      });
  }
  _ensureOpen() {
    if (this._closedPromiseResolve)
      return !0;
    throw new Error("AsyncQueue is closed");
  }
}

// node_modules/apache-arrow/io/stream.mjs
class R4 extends ZE {
  write(Q) {
    if ((Q = n0(Q)).byteLength > 0)
      return super.write(Q);
  }
  toString(Q = !1) {
    return Q ? O3(this.toUint8Array(!0)) : this.toUint8Array(!1).then(O3);
  }
  toUint8Array(Q = !1) {
    return Q ? ZZ(this._values)[0] : (() => U0(this, void 0, void 0, function* () {
      var J, Y;
      let W = [], K = 0;
      try {
        for (var z = ZX(this), N;N = yield z.next(), !N.done; ) {
          let F = N.value;
          W.push(F), K += F.byteLength;
        }
      } catch (F) {
        J = { error: F };
      } finally {
        try {
          if (N && !N.done && (Y = z.return))
            yield Y.call(z);
        } finally {
          if (J)
            throw J.error;
        }
      }
      return ZZ(W, K)[0];
    }))();
  }
}

class j4 {
  constructor(Q) {
    if (Q)
      this.source = new HD(y8.fromIterable(Q));
  }
  [Symbol.iterator]() {
    return this;
  }
  next(Q) {
    return this.source.next(Q);
  }
  throw(Q) {
    return this.source.throw(Q);
  }
  return(Q) {
    return this.source.return(Q);
  }
  peek(Q) {
    return this.source.peek(Q);
  }
  read(Q) {
    return this.source.read(Q);
  }
}

class IZ {
  constructor(Q) {
    if (Q instanceof IZ)
      this.source = Q.source;
    else if (Q instanceof R4)
      this.source = new _J(y8.fromAsyncIterable(Q));
    else if (v5(Q))
      this.source = new _J(y8.fromNodeStream(Q));
    else if (w3(Q))
      this.source = new _J(y8.fromDOMStream(Q));
    else if (g5(Q))
      this.source = new _J(y8.fromDOMStream(Q.body));
    else if (XX(Q))
      this.source = new _J(y8.fromIterable(Q));
    else if (QZ(Q))
      this.source = new _J(y8.fromAsyncIterable(Q));
    else if (OZ(Q))
      this.source = new _J(y8.fromAsyncIterable(Q));
  }
  [Symbol.asyncIterator]() {
    return this;
  }
  next(Q) {
    return this.source.next(Q);
  }
  throw(Q) {
    return this.source.throw(Q);
  }
  return(Q) {
    return this.source.return(Q);
  }
  get closed() {
    return this.source.closed;
  }
  cancel(Q) {
    return this.source.cancel(Q);
  }
  peek(Q) {
    return this.source.peek(Q);
  }
  read(Q) {
    return this.source.read(Q);
  }
}

class HD {
  constructor(Q) {
    this.source = Q;
  }
  cancel(Q) {
    this.return(Q);
  }
  peek(Q) {
    return this.next(Q, "peek").value;
  }
  read(Q) {
    return this.next(Q, "read").value;
  }
  next(Q, J = "read") {
    return this.source.next({ cmd: J, size: Q });
  }
  throw(Q) {
    return Object.create(this.source.throw && this.source.throw(Q) || Y6);
  }
  return(Q) {
    return Object.create(this.source.return && this.source.return(Q) || Y6);
  }
}

class _J {
  constructor(Q) {
    this.source = Q, this._closedPromise = new Promise((J) => this._closedPromiseResolve = J);
  }
  cancel(Q) {
    return U0(this, void 0, void 0, function* () {
      yield this.return(Q);
    });
  }
  get closed() {
    return this._closedPromise;
  }
  read(Q) {
    return U0(this, void 0, void 0, function* () {
      return (yield this.next(Q, "read")).value;
    });
  }
  peek(Q) {
    return U0(this, void 0, void 0, function* () {
      return (yield this.next(Q, "peek")).value;
    });
  }
  next(Q, J = "read") {
    return U0(this, void 0, void 0, function* () {
      return yield this.source.next({ cmd: J, size: Q });
    });
  }
  throw(Q) {
    return U0(this, void 0, void 0, function* () {
      let J = this.source.throw && (yield this.source.throw(Q)) || Y6;
      return this._closedPromiseResolve && this._closedPromiseResolve(), this._closedPromiseResolve = void 0, Object.create(J);
    });
  }
  return(Q) {
    return U0(this, void 0, void 0, function* () {
      let J = this.source.return && (yield this.source.return(Q)) || Y6;
      return this._closedPromiseResolve && this._closedPromiseResolve(), this._closedPromiseResolve = void 0, Object.create(J);
    });
  }
}

// node_modules/apache-arrow/io/file.mjs
class zH extends j4 {
  constructor(Q, J) {
    super();
    this.position = 0, this.buffer = n0(Q), this.size = typeof J === "undefined" ? this.buffer.byteLength : J;
  }
  readInt32(Q) {
    let { buffer: J, byteOffset: Y } = this.readAt(Q, 4);
    return new DataView(J, Y).getInt32(0, !0);
  }
  seek(Q) {
    return this.position = Math.min(Q, this.size), Q < this.size;
  }
  read(Q) {
    let { buffer: J, size: Y, position: W } = this;
    if (J && W < Y) {
      if (typeof Q !== "number")
        Q = Number.POSITIVE_INFINITY;
      return this.position = Math.min(Y, W + Math.min(Y - W, Q)), J.subarray(W, this.position);
    }
    return null;
  }
  readAt(Q, J) {
    let Y = this.buffer, W = Math.min(this.size, Q + J);
    return Y ? Y.subarray(Q, W) : new Uint8Array(J);
  }
  close() {
    this.buffer && (this.buffer = null);
  }
  throw(Q) {
    return this.close(), { done: !0, value: Q };
  }
  return(Q) {
    return this.close(), { done: !0, value: Q };
  }
}

class S$ extends IZ {
  constructor(Q, J) {
    super();
    if (this.position = 0, this._handle = Q, typeof J === "number")
      this.size = J;
    else
      this._pending = (() => U0(this, void 0, void 0, function* () {
        this.size = (yield Q.stat()).size, delete this._pending;
      }))();
  }
  readInt32(Q) {
    return U0(this, void 0, void 0, function* () {
      let { buffer: J, byteOffset: Y } = yield this.readAt(Q, 4);
      return new DataView(J, Y).getInt32(0, !0);
    });
  }
  seek(Q) {
    return U0(this, void 0, void 0, function* () {
      return this._pending && (yield this._pending), this.position = Math.min(Q, this.size), Q < this.size;
    });
  }
  read(Q) {
    return U0(this, void 0, void 0, function* () {
      this._pending && (yield this._pending);
      let { _handle: J, size: Y, position: W } = this;
      if (J && W < Y) {
        if (typeof Q !== "number")
          Q = Number.POSITIVE_INFINITY;
        let K = W, z = 0, N = 0, F = Math.min(Y, K + Math.min(Y - K, Q)), L = new Uint8Array(Math.max(0, (this.position = F) - K));
        while ((K += N) < F && (z += N) < L.byteLength)
          ({ bytesRead: N } = yield J.read(L, z, L.byteLength - z, K));
        return L;
      }
      return null;
    });
  }
  readAt(Q, J) {
    return U0(this, void 0, void 0, function* () {
      this._pending && (yield this._pending);
      let { _handle: Y, size: W } = this;
      if (Y && Q + J < W) {
        let K = Math.min(W, Q + J), z = new Uint8Array(K - Q);
        return (yield Y.read(z, 0, J, Q)).buffer;
      }
      return new Uint8Array(J);
    });
  }
  close() {
    return U0(this, void 0, void 0, function* () {
      let Q = this._handle;
      this._handle = null, Q && (yield Q.close());
    });
  }
  throw(Q) {
    return U0(this, void 0, void 0, function* () {
      return yield this.close(), { done: !0, value: Q };
    });
  }
  return(Q) {
    return U0(this, void 0, void 0, function* () {
      return yield this.close(), { done: !0, value: Q };
    });
  }
}

// node_modules/apache-arrow/util/int.mjs
var JE = {};
sY(JE, {
  Uint64: () => l1,
  Int64: () => JQ,
  Int128: () => _Z,
  BaseInt64: () => NH
});
function zq(Q) {
  if (Q < 0)
    Q = 4294967295 + Q + 1;
  return `0x${Q.toString(16)}`;
}
var Nq = 8, XE = [
  1,
  10,
  100,
  1000,
  1e4,
  1e5,
  1e6,
  1e7,
  1e8
];

class NH {
  constructor(Q) {
    this.buffer = Q;
  }
  high() {
    return this.buffer[1];
  }
  low() {
    return this.buffer[0];
  }
  _times(Q) {
    let J = new Uint32Array([
      this.buffer[1] >>> 16,
      this.buffer[1] & 65535,
      this.buffer[0] >>> 16,
      this.buffer[0] & 65535
    ]), Y = new Uint32Array([
      Q.buffer[1] >>> 16,
      Q.buffer[1] & 65535,
      Q.buffer[0] >>> 16,
      Q.buffer[0] & 65535
    ]), W = J[3] * Y[3];
    this.buffer[0] = W & 65535;
    let K = W >>> 16;
    return W = J[2] * Y[3], K += W, W = J[3] * Y[2] >>> 0, K += W, this.buffer[0] += K << 16, this.buffer[1] = K >>> 0 < W ? 65536 : 0, this.buffer[1] += K >>> 16, this.buffer[1] += J[1] * Y[3] + J[2] * Y[2] + J[3] * Y[1], this.buffer[1] += J[0] * Y[3] + J[1] * Y[2] + J[2] * Y[1] + J[3] * Y[0] << 16, this;
  }
  _plus(Q) {
    let J = this.buffer[0] + Q.buffer[0] >>> 0;
    if (this.buffer[1] += Q.buffer[1], J < this.buffer[0] >>> 0)
      ++this.buffer[1];
    this.buffer[0] = J;
  }
  lessThan(Q) {
    return this.buffer[1] < Q.buffer[1] || this.buffer[1] === Q.buffer[1] && this.buffer[0] < Q.buffer[0];
  }
  equals(Q) {
    return this.buffer[1] === Q.buffer[1] && this.buffer[0] == Q.buffer[0];
  }
  greaterThan(Q) {
    return Q.lessThan(this);
  }
  hex() {
    return `${zq(this.buffer[1])} ${zq(this.buffer[0])}`;
  }
}

class l1 extends NH {
  times(Q) {
    return this._times(Q), this;
  }
  plus(Q) {
    return this._plus(Q), this;
  }
  static from(Q, J = new Uint32Array(2)) {
    return l1.fromString(typeof Q === "string" ? Q : Q.toString(), J);
  }
  static fromNumber(Q, J = new Uint32Array(2)) {
    return l1.fromString(Q.toString(), J);
  }
  static fromString(Q, J = new Uint32Array(2)) {
    let Y = Q.length, W = new l1(J);
    for (let K = 0;K < Y; ) {
      let z = Nq < Y - K ? Nq : Y - K, N = new l1(new Uint32Array([Number.parseInt(Q.slice(K, K + z), 10), 0])), F = new l1(new Uint32Array([XE[z], 0]));
      W.times(F), W.plus(N), K += z;
    }
    return W;
  }
  static convertArray(Q) {
    let J = new Uint32Array(Q.length * 2);
    for (let Y = -1, W = Q.length;++Y < W; )
      l1.from(Q[Y], new Uint32Array(J.buffer, J.byteOffset + 2 * Y * 4, 2));
    return J;
  }
  static multiply(Q, J) {
    return new l1(new Uint32Array(Q.buffer)).times(J);
  }
  static add(Q, J) {
    return new l1(new Uint32Array(Q.buffer)).plus(J);
  }
}

class JQ extends NH {
  negate() {
    if (this.buffer[0] = ~this.buffer[0] + 1, this.buffer[1] = ~this.buffer[1], this.buffer[0] == 0)
      ++this.buffer[1];
    return this;
  }
  times(Q) {
    return this._times(Q), this;
  }
  plus(Q) {
    return this._plus(Q), this;
  }
  lessThan(Q) {
    let J = this.buffer[1] << 0, Y = Q.buffer[1] << 0;
    return J < Y || J === Y && this.buffer[0] < Q.buffer[0];
  }
  static from(Q, J = new Uint32Array(2)) {
    return JQ.fromString(typeof Q === "string" ? Q : Q.toString(), J);
  }
  static fromNumber(Q, J = new Uint32Array(2)) {
    return JQ.fromString(Q.toString(), J);
  }
  static fromString(Q, J = new Uint32Array(2)) {
    let Y = Q.startsWith("-"), W = Q.length, K = new JQ(J);
    for (let z = Y ? 1 : 0;z < W; ) {
      let N = Nq < W - z ? Nq : W - z, F = new JQ(new Uint32Array([Number.parseInt(Q.slice(z, z + N), 10), 0])), L = new JQ(new Uint32Array([XE[N], 0]));
      K.times(L), K.plus(F), z += N;
    }
    return Y ? K.negate() : K;
  }
  static convertArray(Q) {
    let J = new Uint32Array(Q.length * 2);
    for (let Y = -1, W = Q.length;++Y < W; )
      JQ.from(Q[Y], new Uint32Array(J.buffer, J.byteOffset + 2 * Y * 4, 2));
    return J;
  }
  static multiply(Q, J) {
    return new JQ(new Uint32Array(Q.buffer)).times(J);
  }
  static add(Q, J) {
    return new JQ(new Uint32Array(Q.buffer)).plus(J);
  }
}

class _Z {
  constructor(Q) {
    this.buffer = Q;
  }
  high() {
    return new JQ(new Uint32Array(this.buffer.buffer, this.buffer.byteOffset + 8, 2));
  }
  low() {
    return new JQ(new Uint32Array(this.buffer.buffer, this.buffer.byteOffset, 2));
  }
  negate() {
    if (this.buffer[0] = ~this.buffer[0] + 1, this.buffer[1] = ~this.buffer[1], this.buffer[2] = ~this.buffer[2], this.buffer[3] = ~this.buffer[3], this.buffer[0] == 0)
      ++this.buffer[1];
    if (this.buffer[1] == 0)
      ++this.buffer[2];
    if (this.buffer[2] == 0)
      ++this.buffer[3];
    return this;
  }
  times(Q) {
    let J = new l1(new Uint32Array([this.buffer[3], 0])), Y = new l1(new Uint32Array([this.buffer[2], 0])), W = new l1(new Uint32Array([this.buffer[1], 0])), K = new l1(new Uint32Array([this.buffer[0], 0])), z = new l1(new Uint32Array([Q.buffer[3], 0])), N = new l1(new Uint32Array([Q.buffer[2], 0])), F = new l1(new Uint32Array([Q.buffer[1], 0])), L = new l1(new Uint32Array([Q.buffer[0], 0])), w = l1.multiply(K, L);
    this.buffer[0] = w.low();
    let D = new l1(new Uint32Array([w.high(), 0]));
    return w = l1.multiply(W, L), D.plus(w), w = l1.multiply(K, F), D.plus(w), this.buffer[1] = D.low(), this.buffer[3] = D.lessThan(w) ? 1 : 0, this.buffer[2] = D.high(), new l1(new Uint32Array(this.buffer.buffer, this.buffer.byteOffset + 8, 2)).plus(l1.multiply(Y, L)).plus(l1.multiply(W, F)).plus(l1.multiply(K, N)), this.buffer[3] += l1.multiply(J, L).plus(l1.multiply(Y, F)).plus(l1.multiply(W, N)).plus(l1.multiply(K, z)).low(), this;
  }
  plus(Q) {
    let J = new Uint32Array(4);
    if (J[3] = this.buffer[3] + Q.buffer[3] >>> 0, J[2] = this.buffer[2] + Q.buffer[2] >>> 0, J[1] = this.buffer[1] + Q.buffer[1] >>> 0, J[0] = this.buffer[0] + Q.buffer[0] >>> 0, J[0] < this.buffer[0] >>> 0)
      ++J[1];
    if (J[1] < this.buffer[1] >>> 0)
      ++J[2];
    if (J[2] < this.buffer[2] >>> 0)
      ++J[3];
    return this.buffer[3] = J[3], this.buffer[2] = J[2], this.buffer[1] = J[1], this.buffer[0] = J[0], this;
  }
  hex() {
    return `${zq(this.buffer[3])} ${zq(this.buffer[2])} ${zq(this.buffer[1])} ${zq(this.buffer[0])}`;
  }
  static multiply(Q, J) {
    return new _Z(new Uint32Array(Q.buffer)).times(J);
  }
  static add(Q, J) {
    return new _Z(new Uint32Array(Q.buffer)).plus(J);
  }
  static from(Q, J = new Uint32Array(4)) {
    return _Z.fromString(typeof Q === "string" ? Q : Q.toString(), J);
  }
  static fromNumber(Q, J = new Uint32Array(4)) {
    return _Z.fromString(Q.toString(), J);
  }
  static fromString(Q, J = new Uint32Array(4)) {
    let Y = Q.startsWith("-"), W = Q.length, K = new _Z(J);
    for (let z = Y ? 1 : 0;z < W; ) {
      let N = Nq < W - z ? Nq : W - z, F = new _Z(new Uint32Array([Number.parseInt(Q.slice(z, z + N), 10), 0, 0, 0])), L = new _Z(new Uint32Array([XE[N], 0, 0, 0]));
      K.times(L), K.plus(F), z += N;
    }
    return Y ? K.negate() : K;
  }
  static convertArray(Q) {
    let J = new Uint32Array(Q.length * 4);
    for (let Y = -1, W = Q.length;++Y < W; )
      _Z.from(Q[Y], new Uint32Array(J.buffer, J.byteOffset + 16 * Y, 4));
    return J;
  }
}

// node_modules/apache-arrow/visitor/vectorloader.mjs
class EH extends y0 {
  constructor(Q, J, Y, W) {
    super();
    this.nodesIndex = -1, this.buffersIndex = -1, this.bytes = Q, this.nodes = J, this.buffers = Y, this.dictionaries = W;
  }
  visit(Q) {
    return super.visit(Q instanceof q1 ? Q.type : Q);
  }
  visitNull(Q, { length: J } = this.nextFieldNode()) {
    return e0({ type: Q, length: J });
  }
  visitBool(Q, { length: J, nullCount: Y } = this.nextFieldNode()) {
    return e0({ type: Q, length: J, nullCount: Y, nullBitmap: this.readNullBitmap(Q, Y), data: this.readData(Q) });
  }
  visitInt(Q, { length: J, nullCount: Y } = this.nextFieldNode()) {
    return e0({ type: Q, length: J, nullCount: Y, nullBitmap: this.readNullBitmap(Q, Y), data: this.readData(Q) });
  }
  visitFloat(Q, { length: J, nullCount: Y } = this.nextFieldNode()) {
    return e0({ type: Q, length: J, nullCount: Y, nullBitmap: this.readNullBitmap(Q, Y), data: this.readData(Q) });
  }
  visitUtf8(Q, { length: J, nullCount: Y } = this.nextFieldNode()) {
    return e0({ type: Q, length: J, nullCount: Y, nullBitmap: this.readNullBitmap(Q, Y), valueOffsets: this.readOffsets(Q), data: this.readData(Q) });
  }
  visitBinary(Q, { length: J, nullCount: Y } = this.nextFieldNode()) {
    return e0({ type: Q, length: J, nullCount: Y, nullBitmap: this.readNullBitmap(Q, Y), valueOffsets: this.readOffsets(Q), data: this.readData(Q) });
  }
  visitFixedSizeBinary(Q, { length: J, nullCount: Y } = this.nextFieldNode()) {
    return e0({ type: Q, length: J, nullCount: Y, nullBitmap: this.readNullBitmap(Q, Y), data: this.readData(Q) });
  }
  visitDate(Q, { length: J, nullCount: Y } = this.nextFieldNode()) {
    return e0({ type: Q, length: J, nullCount: Y, nullBitmap: this.readNullBitmap(Q, Y), data: this.readData(Q) });
  }
  visitTimestamp(Q, { length: J, nullCount: Y } = this.nextFieldNode()) {
    return e0({ type: Q, length: J, nullCount: Y, nullBitmap: this.readNullBitmap(Q, Y), data: this.readData(Q) });
  }
  visitTime(Q, { length: J, nullCount: Y } = this.nextFieldNode()) {
    return e0({ type: Q, length: J, nullCount: Y, nullBitmap: this.readNullBitmap(Q, Y), data: this.readData(Q) });
  }
  visitDecimal(Q, { length: J, nullCount: Y } = this.nextFieldNode()) {
    return e0({ type: Q, length: J, nullCount: Y, nullBitmap: this.readNullBitmap(Q, Y), data: this.readData(Q) });
  }
  visitList(Q, { length: J, nullCount: Y } = this.nextFieldNode()) {
    return e0({ type: Q, length: J, nullCount: Y, nullBitmap: this.readNullBitmap(Q, Y), valueOffsets: this.readOffsets(Q), child: this.visit(Q.children[0]) });
  }
  visitStruct(Q, { length: J, nullCount: Y } = this.nextFieldNode()) {
    return e0({ type: Q, length: J, nullCount: Y, nullBitmap: this.readNullBitmap(Q, Y), children: this.visitMany(Q.children) });
  }
  visitUnion(Q) {
    return Q.mode === k6.Sparse ? this.visitSparseUnion(Q) : this.visitDenseUnion(Q);
  }
  visitDenseUnion(Q, { length: J, nullCount: Y } = this.nextFieldNode()) {
    return e0({ type: Q, length: J, nullCount: Y, nullBitmap: this.readNullBitmap(Q, Y), typeIds: this.readTypeIds(Q), valueOffsets: this.readOffsets(Q), children: this.visitMany(Q.children) });
  }
  visitSparseUnion(Q, { length: J, nullCount: Y } = this.nextFieldNode()) {
    return e0({ type: Q, length: J, nullCount: Y, nullBitmap: this.readNullBitmap(Q, Y), typeIds: this.readTypeIds(Q), children: this.visitMany(Q.children) });
  }
  visitDictionary(Q, { length: J, nullCount: Y } = this.nextFieldNode()) {
    return e0({ type: Q, length: J, nullCount: Y, nullBitmap: this.readNullBitmap(Q, Y), data: this.readData(Q.indices), dictionary: this.readDictionary(Q) });
  }
  visitInterval(Q, { length: J, nullCount: Y } = this.nextFieldNode()) {
    return e0({ type: Q, length: J, nullCount: Y, nullBitmap: this.readNullBitmap(Q, Y), data: this.readData(Q) });
  }
  visitFixedSizeList(Q, { length: J, nullCount: Y } = this.nextFieldNode()) {
    return e0({ type: Q, length: J, nullCount: Y, nullBitmap: this.readNullBitmap(Q, Y), child: this.visit(Q.children[0]) });
  }
  visitMap(Q, { length: J, nullCount: Y } = this.nextFieldNode()) {
    return e0({ type: Q, length: J, nullCount: Y, nullBitmap: this.readNullBitmap(Q, Y), valueOffsets: this.readOffsets(Q), child: this.visit(Q.children[0]) });
  }
  nextFieldNode() {
    return this.nodes[++this.nodesIndex];
  }
  nextBufferRange() {
    return this.buffers[++this.buffersIndex];
  }
  readNullBitmap(Q, J, Y = this.nextBufferRange()) {
    return J > 0 && this.readData(Q, Y) || new Uint8Array(0);
  }
  readOffsets(Q, J) {
    return this.readData(Q, J);
  }
  readTypeIds(Q, J) {
    return this.readData(Q, J);
  }
  readData(Q, { length: J, offset: Y } = this.nextBufferRange()) {
    return this.bytes.subarray(Y, Y + J);
  }
  readDictionary(Q) {
    return this.dictionaries.get(Q.id);
  }
}

class $E extends EH {
  constructor(Q, J, Y, W) {
    super(new Uint8Array(0), J, Y, W);
    this.sources = Q;
  }
  readNullBitmap(Q, J, { offset: Y } = this.nextBufferRange()) {
    return J <= 0 ? new Uint8Array(0) : j$(this.sources[Y]);
  }
  readOffsets(Q, { offset: J } = this.nextBufferRange()) {
    return G1(Uint8Array, G1(Int32Array, this.sources[J]));
  }
  readTypeIds(Q, { offset: J } = this.nextBufferRange()) {
    return G1(Uint8Array, G1(Q.ArrayType, this.sources[J]));
  }
  readData(Q, { offset: J } = this.nextBufferRange()) {
    let { sources: Y } = this;
    if (C0.isTimestamp(Q))
      return G1(Uint8Array, JQ.convertArray(Y[J]));
    else if ((C0.isInt(Q) || C0.isTime(Q)) && Q.bitWidth === 64)
      return G1(Uint8Array, JQ.convertArray(Y[J]));
    else if (C0.isDate(Q) && Q.unit === f8.MILLISECOND)
      return G1(Uint8Array, JQ.convertArray(Y[J]));
    else if (C0.isDecimal(Q))
      return G1(Uint8Array, _Z.convertArray(Y[J]));
    else if (C0.isBinary(Q) || C0.isFixedSizeBinary(Q))
      return Sh(Y[J]);
    else if (C0.isBool(Q))
      return j$(Y[J]);
    else if (C0.isUtf8(Q))
      return WJ(Y[J].join(""));
    return G1(Uint8Array, G1(Q.ArrayType, Y[J].map((W) => +W)));
  }
}
function Sh(Q) {
  let J = Q.join(""), Y = new Uint8Array(J.length / 2);
  for (let W = 0;W < J.length; W += 2)
    Y[W >> 1] = Number.parseInt(J.slice(W, W + 2), 16);
  return Y;
}

// node_modules/apache-arrow/builder/binary.mjs
class f3 extends D4 {
  constructor(Q) {
    super(Q);
    this._values = new C$(new Uint8Array(0));
  }
  get byteLength() {
    let Q = this._pendingLength + this.length * 4;
    return this._offsets && (Q += this._offsets.byteLength), this._values && (Q += this._values.byteLength), this._nulls && (Q += this._nulls.byteLength), Q;
  }
  setValue(Q, J) {
    return super.setValue(Q, n0(J));
  }
  _flushPending(Q, J) {
    let Y = this._offsets, W = this._values.reserve(J).buffer, K = 0;
    for (let [z, N] of Q)
      if (N === void 0)
        Y.set(z, 0);
      else {
        let F = N.length;
        W.set(N, K), Y.set(z, F), K += F;
      }
  }
}

// node_modules/apache-arrow/builder/bool.mjs
class YE extends U6 {
  constructor(Q) {
    super(Q);
    this._values = new S3;
  }
  setValue(Q, J) {
    this._values.set(Q, +J);
  }
}

// node_modules/apache-arrow/builder/date.mjs
class Eq extends b8 {
}
Eq.prototype._setValue = dN;

class FH extends Eq {
}
FH.prototype._setValue = m5;

class UH extends Eq {
}
UH.prototype._setValue = b5;

// node_modules/apache-arrow/builder/decimal.mjs
class PH extends b8 {
}
PH.prototype._setValue = sN;

// node_modules/apache-arrow/builder/dictionary.mjs
class qE extends U6 {
  constructor({ type: Q, nullValues: J, dictionaryHashFunction: Y }) {
    super({ type: new MZ(Q.dictionary, Q.indices, Q.id, Q.isOrdered) });
    if (this._nulls = null, this._dictionaryOffset = 0, this._keysToIndices = Object.create(null), this.indices = I$({ type: this.type.indices, nullValues: J }), this.dictionary = I$({ type: this.type.dictionary, nullValues: null }), typeof Y === "function")
      this.valueToKey = Y;
  }
  get values() {
    return this.indices.values;
  }
  get nullCount() {
    return this.indices.nullCount;
  }
  get nullBitmap() {
    return this.indices.nullBitmap;
  }
  get byteLength() {
    return this.indices.byteLength + this.dictionary.byteLength;
  }
  get reservedLength() {
    return this.indices.reservedLength + this.dictionary.reservedLength;
  }
  get reservedByteLength() {
    return this.indices.reservedByteLength + this.dictionary.reservedByteLength;
  }
  isValid(Q) {
    return this.indices.isValid(Q);
  }
  setValid(Q, J) {
    let Y = this.indices;
    return J = Y.setValid(Q, J), this.length = Y.length, J;
  }
  setValue(Q, J) {
    let Y = this._keysToIndices, W = this.valueToKey(J), K = Y[W];
    if (K === void 0)
      Y[W] = K = this._dictionaryOffset + this.dictionary.append(J).length - 1;
    return this.indices.setValue(Q, K);
  }
  flush() {
    let Q = this.type, J = this._dictionary, Y = this.dictionary.toVector(), W = this.indices.flush().clone(Q);
    return W.dictionary = J ? J.concat(Y) : Y, this.finished || (this._dictionaryOffset += Y.length), this._dictionary = W.dictionary, this.clear(), W;
  }
  finish() {
    return this.indices.finish(), this.dictionary.finish(), this._dictionaryOffset = 0, this._keysToIndices = Object.create(null), super.finish();
  }
  clear() {
    return this.indices.clear(), this.dictionary.clear(), super.clear();
  }
  valueToKey(Q) {
    return typeof Q === "string" ? Q : `${Q}`;
  }
}

// node_modules/apache-arrow/builder/fixedsizebinary.mjs
class AH extends b8 {
}
AH.prototype._setValue = pN;

// node_modules/apache-arrow/builder/fixedsizelist.mjs
class WE extends U6 {
  setValue(Q, J) {
    let [Y] = this.children, W = Q * this.stride;
    for (let K = -1, z = J.length;++K < z; )
      Y.set(W + K, J[K]);
  }
  addChild(Q, J = "0") {
    if (this.numChildren > 0)
      throw new Error("FixedSizeListBuilder can only have one child.");
    let Y = this.children.push(Q);
    return this.type = new bX(this.type.listSize, new q1(J, Q.type, !0)), Y;
  }
}

// node_modules/apache-arrow/builder/float.mjs
class Fq extends b8 {
  setValue(Q, J) {
    this._values.set(Q, J);
  }
}

class KE extends Fq {
  setValue(Q, J) {
    super.setValue(Q, R3(J));
  }
}

class HE extends Fq {
}

class GE extends Fq {
}

// node_modules/apache-arrow/builder/interval.mjs
class Uq extends b8 {
}
Uq.prototype._setValue = oN;

class LH extends Uq {
}
LH.prototype._setValue = a5;

class OH extends Uq {
}
OH.prototype._setValue = r5;

// node_modules/apache-arrow/builder/int.mjs
class KX extends b8 {
  setValue(Q, J) {
    this._values.set(Q, J);
  }
}

class zE extends KX {
}

class NE extends KX {
}

class EE extends KX {
}

class FE extends KX {
}

class UE extends KX {
}

class PE extends KX {
}

class AE extends KX {
}

class LE extends KX {
}

// node_modules/apache-arrow/builder/list.mjs
class OE extends D4 {
  constructor(Q) {
    super(Q);
    this._offsets = new I3;
  }
  addChild(Q, J = "0") {
    if (this.numChildren > 0)
      throw new Error("ListBuilder can only have one child.");
    return this.children[this.numChildren] = Q, this.type = new fX(new q1(J, Q.type, !0)), this.numChildren - 1;
  }
  _flushPending(Q) {
    let J = this._offsets, [Y] = this.children;
    for (let [W, K] of Q)
      if (typeof K === "undefined")
        J.set(W, 0);
      else {
        let z = K.length, N = J.set(W, z).buffer[W];
        for (let F = -1;++F < z; )
          Y.set(N + F, K[F]);
      }
  }
}

// node_modules/apache-arrow/builder/map.mjs
class wE extends D4 {
  set(Q, J) {
    return super.set(Q, J);
  }
  setValue(Q, J) {
    let Y = J instanceof Map ? J : new Map(Object.entries(J)), W = this._pending || (this._pending = /* @__PURE__ */ new Map), K = W.get(Q);
    K && (this._pendingLength -= K.size), this._pendingLength += Y.size, W.set(Q, Y);
  }
  addChild(Q, J = `${this.numChildren}`) {
    if (this.numChildren > 0)
      throw new Error("ListBuilder can only have one child.");
    return this.children[this.numChildren] = Q, this.type = new uX(new q1(J, Q.type, !0), this.type.keysSorted), this.numChildren - 1;
  }
  _flushPending(Q) {
    let J = this._offsets, [Y] = this.children;
    for (let [W, K] of Q)
      if (K === void 0)
        J.set(W, 0);
      else {
        let { [W]: z, [W + 1]: N } = J.set(W, K.size).buffer;
        for (let F of K.entries())
          if (Y.set(z, F), ++z >= N)
            break;
      }
  }
}

// node_modules/apache-arrow/builder/null.mjs
class ME extends U6 {
  setValue(Q, J) {}
  setValid(Q, J) {
    return this.length = Math.max(Q + 1, this.length), J;
  }
}

// node_modules/apache-arrow/builder/struct.mjs
class DE extends U6 {
  setValue(Q, J) {
    let { children: Y, type: W } = this;
    switch (Array.isArray(J) || J.constructor) {
      case !0:
        return W.children.forEach((K, z) => Y[z].set(Q, J[z]));
      case Map:
        return W.children.forEach((K, z) => Y[z].set(Q, J.get(K.name)));
      default:
        return W.children.forEach((K, z) => Y[z].set(Q, J[K.name]));
    }
  }
  setValid(Q, J) {
    if (!super.setValid(Q, J))
      this.children.forEach((Y) => Y.setValid(Q, J));
    return J;
  }
  addChild(Q, J = `${this.numChildren}`) {
    let Y = this.children.push(Q);
    return this.type = new H6([...this.type.children, new q1(J, Q.type, !0)]), Y;
  }
}

// node_modules/apache-arrow/builder/timestamp.mjs
class TJ extends b8 {
}
TJ.prototype._setValue = lN;

class wH extends TJ {
}
wH.prototype._setValue = u5;

class MH extends TJ {
}
MH.prototype._setValue = c5;

class DH extends TJ {
}
DH.prototype._setValue = p5;

class kH extends TJ {
}
kH.prototype._setValue = d5;

// node_modules/apache-arrow/builder/time.mjs
class gJ extends b8 {
}
gJ.prototype._setValue = nN;

class RH extends gJ {
}
RH.prototype._setValue = l5;

class jH extends gJ {
}
jH.prototype._setValue = n5;

class BH extends gJ {
}
BH.prototype._setValue = s5;

class CH extends gJ {
}
CH.prototype._setValue = o5;

// node_modules/apache-arrow/builder/union.mjs
class m3 extends U6 {
  constructor(Q) {
    super(Q);
    if (this._typeIds = new wJ(new Int8Array(0), 1), typeof Q.valueToChildTypeId === "function")
      this._valueToChildTypeId = Q.valueToChildTypeId;
  }
  get typeIdToChildIndex() {
    return this.type.typeIdToChildIndex;
  }
  append(Q, J) {
    return this.set(this.length, Q, J);
  }
  set(Q, J, Y) {
    if (Y === void 0)
      Y = this._valueToChildTypeId(this, J, Q);
    if (this.setValid(Q, this.isValid(J)))
      this.setValue(Q, J, Y);
    return this;
  }
  setValue(Q, J, Y) {
    this._typeIds.set(Q, Y);
    let W = this.type.typeIdToChildIndex[Y], K = this.children[W];
    K === null || K === void 0 || K.set(Q, J);
  }
  addChild(Q, J = `${this.children.length}`) {
    let Y = this.children.push(Q), { type: { children: W, mode: K, typeIds: z } } = this, N = [...W, new q1(J, Q.type)];
    return this.type = new mX(K, [...z, Y], N), Y;
  }
  _valueToChildTypeId(Q, J, Y) {
    throw new Error("Cannot map UnionBuilder value to child typeId. Pass the `childTypeId` as the second argument to unionBuilder.append(), or supply a `valueToChildTypeId` function as part of the UnionBuilder constructor options.");
  }
}

class kE extends m3 {
}

class RE extends m3 {
  constructor(Q) {
    super(Q);
    this._offsets = new wJ(new Int32Array(0));
  }
  setValue(Q, J, Y) {
    let W = this._typeIds.set(Q, Y).buffer[Q], K = this.getChildAt(this.type.typeIdToChildIndex[W]), z = this._offsets.set(Q, K.length).buffer[Q];
    K === null || K === void 0 || K.set(z, J);
  }
}

// node_modules/apache-arrow/builder/utf8.mjs
class VH extends D4 {
  constructor(Q) {
    super(Q);
    this._values = new C$(new Uint8Array(0));
  }
  get byteLength() {
    let Q = this._pendingLength + this.length * 4;
    return this._offsets && (Q += this._offsets.byteLength), this._values && (Q += this._values.byteLength), this._nulls && (Q += this._nulls.byteLength), Q;
  }
  setValue(Q, J) {
    return super.setValue(Q, WJ(J));
  }
  _flushPending(Q, J) {}
}
VH.prototype._flushPending = f3.prototype._flushPending;

// node_modules/apache-arrow/visitor/builderctor.mjs
class GD extends y0 {
  visitNull() {
    return ME;
  }
  visitBool() {
    return YE;
  }
  visitInt() {
    return KX;
  }
  visitInt8() {
    return zE;
  }
  visitInt16() {
    return NE;
  }
  visitInt32() {
    return EE;
  }
  visitInt64() {
    return FE;
  }
  visitUint8() {
    return UE;
  }
  visitUint16() {
    return PE;
  }
  visitUint32() {
    return AE;
  }
  visitUint64() {
    return LE;
  }
  visitFloat() {
    return Fq;
  }
  visitFloat16() {
    return KE;
  }
  visitFloat32() {
    return HE;
  }
  visitFloat64() {
    return GE;
  }
  visitUtf8() {
    return VH;
  }
  visitBinary() {
    return f3;
  }
  visitFixedSizeBinary() {
    return AH;
  }
  visitDate() {
    return Eq;
  }
  visitDateDay() {
    return FH;
  }
  visitDateMillisecond() {
    return UH;
  }
  visitTimestamp() {
    return TJ;
  }
  visitTimestampSecond() {
    return wH;
  }
  visitTimestampMillisecond() {
    return MH;
  }
  visitTimestampMicrosecond() {
    return DH;
  }
  visitTimestampNanosecond() {
    return kH;
  }
  visitTime() {
    return gJ;
  }
  visitTimeSecond() {
    return RH;
  }
  visitTimeMillisecond() {
    return jH;
  }
  visitTimeMicrosecond() {
    return BH;
  }
  visitTimeNanosecond() {
    return CH;
  }
  visitDecimal() {
    return PH;
  }
  visitList() {
    return OE;
  }
  visitStruct() {
    return DE;
  }
  visitUnion() {
    return m3;
  }
  visitDenseUnion() {
    return RE;
  }
  visitSparseUnion() {
    return kE;
  }
  visitDictionary() {
    return qE;
  }
  visitInterval() {
    return Uq;
  }
  visitIntervalDayTime() {
    return LH;
  }
  visitIntervalYearMonth() {
    return OH;
  }
  visitFixedSizeList() {
    return WE;
  }
  visitMap() {
    return wE;
  }
}
var zD = new GD;

// node_modules/apache-arrow/visitor/typecomparator.mjs
class r0 extends y0 {
  compareSchemas(Q, J) {
    return Q === J || J instanceof Q.constructor && this.compareManyFields(Q.fields, J.fields);
  }
  compareManyFields(Q, J) {
    return Q === J || Array.isArray(Q) && Array.isArray(J) && Q.length === J.length && Q.every((Y, W) => this.compareFields(Y, J[W]));
  }
  compareFields(Q, J) {
    return Q === J || J instanceof Q.constructor && Q.name === J.name && Q.nullable === J.nullable && this.visit(Q.type, J.type);
  }
}
function mQ(Q, J) {
  return J instanceof Q.constructor;
}
function b3(Q, J) {
  return Q === J || mQ(Q, J);
}
function B4(Q, J) {
  return Q === J || mQ(Q, J) && Q.bitWidth === J.bitWidth && Q.isSigned === J.isSigned;
}
function SH(Q, J) {
  return Q === J || mQ(Q, J) && Q.precision === J.precision;
}
function Ih(Q, J) {
  return Q === J || mQ(Q, J) && Q.byteWidth === J.byteWidth;
}
function jE(Q, J) {
  return Q === J || mQ(Q, J) && Q.unit === J.unit;
}
function u3(Q, J) {
  return Q === J || mQ(Q, J) && Q.unit === J.unit && Q.timezone === J.timezone;
}
function c3(Q, J) {
  return Q === J || mQ(Q, J) && Q.unit === J.unit && Q.bitWidth === J.bitWidth;
}
function _h(Q, J) {
  return Q === J || mQ(Q, J) && Q.children.length === J.children.length && pX.compareManyFields(Q.children, J.children);
}
function Th(Q, J) {
  return Q === J || mQ(Q, J) && Q.children.length === J.children.length && pX.compareManyFields(Q.children, J.children);
}
function BE(Q, J) {
  return Q === J || mQ(Q, J) && Q.mode === J.mode && Q.typeIds.every((Y, W) => Y === J.typeIds[W]) && pX.compareManyFields(Q.children, J.children);
}
function gh(Q, J) {
  return Q === J || mQ(Q, J) && Q.id === J.id && Q.isOrdered === J.isOrdered && pX.visit(Q.indices, J.indices) && pX.visit(Q.dictionary, J.dictionary);
}
function CE(Q, J) {
  return Q === J || mQ(Q, J) && Q.unit === J.unit;
}
function xh(Q, J) {
  return Q === J || mQ(Q, J) && Q.listSize === J.listSize && Q.children.length === J.children.length && pX.compareManyFields(Q.children, J.children);
}
function vh(Q, J) {
  return Q === J || mQ(Q, J) && Q.keysSorted === J.keysSorted && Q.children.length === J.children.length && pX.compareManyFields(Q.children, J.children);
}
r0.prototype.visitNull = b3;
r0.prototype.visitBool = b3;
r0.prototype.visitInt = B4;
r0.prototype.visitInt8 = B4;
r0.prototype.visitInt16 = B4;
r0.prototype.visitInt32 = B4;
r0.prototype.visitInt64 = B4;
r0.prototype.visitUint8 = B4;
r0.prototype.visitUint16 = B4;
r0.prototype.visitUint32 = B4;
r0.prototype.visitUint64 = B4;
r0.prototype.visitFloat = SH;
r0.prototype.visitFloat16 = SH;
r0.prototype.visitFloat32 = SH;
r0.prototype.visitFloat64 = SH;
r0.prototype.visitUtf8 = b3;
r0.prototype.visitBinary = b3;
r0.prototype.visitFixedSizeBinary = Ih;
r0.prototype.visitDate = jE;
r0.prototype.visitDateDay = jE;
r0.prototype.visitDateMillisecond = jE;
r0.prototype.visitTimestamp = u3;
r0.prototype.visitTimestampSecond = u3;
r0.prototype.visitTimestampMillisecond = u3;
r0.prototype.visitTimestampMicrosecond = u3;
r0.prototype.visitTimestampNanosecond = u3;
r0.prototype.visitTime = c3;
r0.prototype.visitTimeSecond = c3;
r0.prototype.visitTimeMillisecond = c3;
r0.prototype.visitTimeMicrosecond = c3;
r0.prototype.visitTimeNanosecond = c3;
r0.prototype.visitDecimal = b3;
r0.prototype.visitList = _h;
r0.prototype.visitStruct = Th;
r0.prototype.visitUnion = BE;
r0.prototype.visitDenseUnion = BE;
r0.prototype.visitSparseUnion = BE;
r0.prototype.visitDictionary = gh;
r0.prototype.visitInterval = CE;
r0.prototype.visitIntervalDayTime = CE;
r0.prototype.visitIntervalYearMonth = CE;
r0.prototype.visitFixedSizeList = xh;
r0.prototype.visitMap = vh;
var pX = new r0;
function _$(Q, J) {
  return pX.compareSchemas(Q, J);
}
function ND(Q, J) {
  return pX.compareFields(Q, J);
}
function ED(Q, J) {
  return pX.visit(Q, J);
}

// node_modules/apache-arrow/factories.mjs
function I$(Q) {
  let J = Q.type, Y = new (zD.getVisitFn(J)())(Q);
  if (J.children && J.children.length > 0) {
    let W = Q.children || [], K = { nullValues: Q.nullValues }, z = Array.isArray(W) ? (N, F) => W[F] || K : ({ name: N }) => W[N] || K;
    for (let [N, F] of J.children.entries()) {
      let { type: L } = F, w = z(F, N);
      Y.children.push(I$(Object.assign(Object.assign({}, w), { type: L })));
    }
  }
  return Y;
}

// node_modules/apache-arrow/util/recordbatch.mjs
function IH(Q, J) {
  return hh(Q, J.map((Y) => Y.data.concat()));
}
function hh(Q, J) {
  let Y = [...Q.fields], W = [], K = { numBatches: J.reduce((R, V) => Math.max(R, V.length), 0) }, z = 0, N = 0, F = -1, L = J.length, w, D = [];
  while (K.numBatches-- > 0) {
    for (N = Number.POSITIVE_INFINITY, F = -1;++F < L; )
      D[F] = w = J[F].shift(), N = Math.min(N, w ? w.length : N);
    if (Number.isFinite(N)) {
      if (D = yh(Y, N, D, J, K), N > 0)
        W[z++] = e0({
          type: new H6(Y),
          length: N,
          nullCount: 0,
          children: D.slice()
        });
    }
  }
  return [
    Q = Q.assign(Y),
    W.map((R) => new z6(Q, R))
  ];
}
function yh(Q, J, Y, W, K) {
  var z;
  let N = (J + 63 & -64) >> 3;
  for (let F = -1, L = W.length;++F < L; ) {
    let w = Y[F], D = w === null || w === void 0 ? void 0 : w.length;
    if (D >= J)
      if (D === J)
        Y[F] = w;
      else
        Y[F] = w.slice(0, J), K.numBatches = Math.max(K.numBatches, W[F].unshift(w.slice(J, D - J)));
    else {
      let R = Q[F];
      Q[F] = R.clone({ nullable: !0 }), Y[F] = (z = w === null || w === void 0 ? void 0 : w._changeLengthAndBackfillNullBitmap(J)) !== null && z !== void 0 ? z : e0({
        type: R.type,
        length: J,
        nullCount: J,
        nullBitmap: new Uint8Array(N)
      });
    }
  }
  return Y;
}

// node_modules/apache-arrow/table.mjs
var FD;

class J8 {
  constructor(...Q) {
    var J, Y;
    if (Q.length === 0)
      return this.batches = [], this.schema = new w1([]), this._offsets = [0], this;
    let W, K;
    if (Q[0] instanceof w1)
      W = Q.shift();
    if (Q[Q.length - 1] instanceof Uint32Array)
      K = Q.pop();
    let z = (F) => {
      if (F) {
        if (F instanceof z6)
          return [F];
        else if (F instanceof J8)
          return F.batches;
        else if (F instanceof d1) {
          if (F.type instanceof H6)
            return [new z6(new w1(F.type.children), F)];
        } else if (Array.isArray(F))
          return F.flatMap((L) => z(L));
        else if (typeof F[Symbol.iterator] === "function")
          return [...F].flatMap((L) => z(L));
        else if (typeof F === "object") {
          let L = Object.keys(F), w = L.map((V) => new Z1([F[V]])), D = new w1(L.map((V, g) => new q1(String(V), w[g].type))), [, R] = IH(D, w);
          return R.length === 0 ? [new z6(F)] : R;
        }
      }
      return [];
    }, N = Q.flatMap((F) => z(F));
    if (W = (Y = W !== null && W !== void 0 ? W : (J = N[0]) === null || J === void 0 ? void 0 : J.schema) !== null && Y !== void 0 ? Y : new w1([]), !(W instanceof w1))
      throw new TypeError("Table constructor expects a [Schema, RecordBatch[]] pair.");
    for (let F of N) {
      if (!(F instanceof z6))
        throw new TypeError("Table constructor expects a [Schema, RecordBatch[]] pair.");
      if (!_$(W, F.schema))
        throw new TypeError("Table and inner RecordBatch schemas must be equivalent.");
    }
    this.schema = W, this.batches = N, this._offsets = K !== null && K !== void 0 ? K : XH(this.data);
  }
  get data() {
    return this.batches.map(({ data: Q }) => Q);
  }
  get numCols() {
    return this.schema.fields.length;
  }
  get numRows() {
    return this.data.reduce((Q, J) => Q + J.length, 0);
  }
  get nullCount() {
    if (this._nullCount === -1)
      this._nullCount = ZH(this.data);
    return this._nullCount;
  }
  isValid(Q) {
    return !1;
  }
  get(Q) {
    return null;
  }
  set(Q, J) {
    return;
  }
  indexOf(Q, J) {
    return -1;
  }
  getByteLength(Q) {
    return 0;
  }
  [Symbol.iterator]() {
    if (this.batches.length > 0)
      return Wq.visit(new Z1(this.data));
    return new Array(0)[Symbol.iterator]();
  }
  toArray() {
    return [...this];
  }
  toString() {
    return `[
  ${this.toArray().join(`,
  `)}
]`;
  }
  concat(...Q) {
    let J = this.schema, Y = this.data.concat(Q.flatMap(({ data: W }) => W));
    return new J8(J, Y.map((W) => new z6(J, W)));
  }
  slice(Q, J) {
    let Y = this.schema;
    [Q, J] = j3({ length: this.numRows }, Q, J);
    let W = JH(this.data, this._offsets, Q, J);
    return new J8(Y, W.map((K) => new z6(Y, K)));
  }
  getChild(Q) {
    return this.getChildAt(this.schema.fields.findIndex((J) => J.name === Q));
  }
  getChildAt(Q) {
    if (Q > -1 && Q < this.schema.fields.length) {
      let J = this.data.map((Y) => Y.children[Q]);
      if (J.length === 0) {
        let { type: Y } = this.schema.fields[Q], W = e0({ type: Y, length: 0, nullCount: 0 });
        J.push(W._changeLengthAndBackfillNullBitmap(this.numRows));
      }
      return new Z1(J);
    }
    return null;
  }
  setChild(Q, J) {
    var Y;
    return this.setChildAt((Y = this.schema.fields) === null || Y === void 0 ? void 0 : Y.findIndex((W) => W.name === Q), J);
  }
  setChildAt(Q, J) {
    let Y = this.schema, W = [...this.batches];
    if (Q > -1 && Q < this.numCols) {
      if (!J)
        J = new Z1([e0({ type: new vQ, length: this.numRows })]);
      let K = Y.fields.slice(), z = K[Q].clone({ type: J.type }), N = this.schema.fields.map((F, L) => this.getChildAt(L));
      [K[Q], N[Q]] = [z, J], [Y, W] = IH(Y, N);
    }
    return new J8(Y, W);
  }
  select(Q) {
    let J = this.schema.fields.reduce((Y, W, K) => Y.set(W.name, K), /* @__PURE__ */ new Map);
    return this.selectAt(Q.map((Y) => J.get(Y)).filter((Y) => Y > -1));
  }
  selectAt(Q) {
    let J = this.schema.selectAt(Q), Y = this.batches.map((W) => W.selectAt(Q));
    return new J8(J, Y);
  }
  assign(Q) {
    let J = this.schema.fields, [Y, W] = Q.schema.fields.reduce((N, F, L) => {
      let [w, D] = N, R = J.findIndex((V) => V.name === F.name);
      return ~R ? D[R] = L : w.push(L), N;
    }, [[], []]), K = this.schema.assign(Q.schema), z = [
      ...J.map((N, F) => [F, W[F]]).map(([N, F]) => F === void 0 ? this.getChildAt(N) : Q.getChildAt(F)),
      ...Y.map((N) => Q.getChildAt(N))
    ].filter(Boolean);
    return new J8(...IH(K, z));
  }
}
FD = Symbol.toStringTag;
J8[FD] = ((Q) => {
  return Q.schema = null, Q.batches = [], Q._offsets = new Uint32Array([0]), Q._nullCount = -1, Q[Symbol.isConcatSpreadable] = !0, Q.isValid = OJ(V3), Q.get = OJ(c6.getVisitFn(I.Struct)), Q.set = $H(m8.getVisitFn(I.Struct)), Q.indexOf = YH(B$.getVisitFn(I.Struct)), Q.getByteLength = OJ($Z.getVisitFn(I.Struct)), "Table";
})(J8.prototype);

// node_modules/apache-arrow/recordbatch.mjs
var PD;

class z6 {
  constructor(...Q) {
    switch (Q.length) {
      case 2: {
        if ([this.schema] = Q, !(this.schema instanceof w1))
          throw new TypeError("RecordBatch constructor expects a [Schema, Data] pair.");
        if ([
          ,
          this.data = e0({
            nullCount: 0,
            type: new H6(this.schema.fields),
            children: this.schema.fields.map((J) => e0({ type: J.type, nullCount: 0 }))
          })
        ] = Q, !(this.data instanceof d1))
          throw new TypeError("RecordBatch constructor expects a [Schema, Data] pair.");
        [this.schema, this.data] = UD(this.schema, this.data.children);
        break;
      }
      case 1: {
        let [J] = Q, { fields: Y, children: W, length: K } = Object.keys(J).reduce((F, L, w) => {
          return F.children[w] = J[L], F.length = Math.max(F.length, J[L].length), F.fields[w] = q1.new({ name: L, type: J[L].type, nullable: !0 }), F;
        }, {
          length: 0,
          fields: new Array,
          children: new Array
        }), z = new w1(Y), N = e0({ type: new H6(Y), length: K, children: W, nullCount: 0 });
        [this.schema, this.data] = UD(z, N.children, K);
        break;
      }
      default:
        throw new TypeError("RecordBatch constructor expects an Object mapping names to child Data, or a [Schema, Data] pair.");
    }
  }
  get dictionaries() {
    return this._dictionaries || (this._dictionaries = AD(this.schema.fields, this.data.children));
  }
  get numCols() {
    return this.schema.fields.length;
  }
  get numRows() {
    return this.data.length;
  }
  get nullCount() {
    return this.data.nullCount;
  }
  isValid(Q) {
    return this.data.getValid(Q);
  }
  get(Q) {
    return c6.visit(this.data, Q);
  }
  set(Q, J) {
    return m8.visit(this.data, Q, J);
  }
  indexOf(Q, J) {
    return B$.visit(this.data, Q, J);
  }
  getByteLength(Q) {
    return $Z.visit(this.data, Q);
  }
  [Symbol.iterator]() {
    return Wq.visit(new Z1([this.data]));
  }
  toArray() {
    return [...this];
  }
  concat(...Q) {
    return new J8(this.schema, [this, ...Q]);
  }
  slice(Q, J) {
    let [Y] = new Z1([this.data]).slice(Q, J).data;
    return new z6(this.schema, Y);
  }
  getChild(Q) {
    var J;
    return this.getChildAt((J = this.schema.fields) === null || J === void 0 ? void 0 : J.findIndex((Y) => Y.name === Q));
  }
  getChildAt(Q) {
    if (Q > -1 && Q < this.schema.fields.length)
      return new Z1([this.data.children[Q]]);
    return null;
  }
  setChild(Q, J) {
    var Y;
    return this.setChildAt((Y = this.schema.fields) === null || Y === void 0 ? void 0 : Y.findIndex((W) => W.name === Q), J);
  }
  setChildAt(Q, J) {
    let Y = this.schema, W = this.data;
    if (Q > -1 && Q < this.numCols) {
      if (!J)
        J = new Z1([e0({ type: new vQ, length: this.numRows })]);
      let K = Y.fields.slice(), z = W.children.slice(), N = K[Q].clone({ type: J.type });
      [K[Q], z[Q]] = [N, J.data[0]], Y = new w1(K, new Map(this.schema.metadata)), W = e0({ type: new H6(K), children: z });
    }
    return new z6(Y, W);
  }
  select(Q) {
    let J = this.schema.select(Q), Y = new H6(J.fields), W = [];
    for (let K of Q) {
      let z = this.schema.fields.findIndex((N) => N.name === K);
      if (~z)
        W[z] = this.data.children[z];
    }
    return new z6(J, e0({ type: Y, length: this.numRows, children: W }));
  }
  selectAt(Q) {
    let J = this.schema.selectAt(Q), Y = Q.map((K) => this.data.children[K]).filter(Boolean), W = e0({ type: new H6(J.fields), length: this.numRows, children: Y });
    return new z6(J, W);
  }
}
PD = Symbol.toStringTag;
z6[PD] = ((Q) => {
  return Q._nullCount = -1, Q[Symbol.isConcatSpreadable] = !0, "RecordBatch";
})(z6.prototype);
function UD(Q, J, Y = J.reduce((W, K) => Math.max(W, K.length), 0)) {
  var W;
  let K = [...Q.fields], z = [...J], N = (Y + 63 & -64) >> 3;
  for (let [F, L] of Q.fields.entries()) {
    let w = J[F];
    if (!w || w.length !== Y)
      K[F] = L.clone({ nullable: !0 }), z[F] = (W = w === null || w === void 0 ? void 0 : w._changeLengthAndBackfillNullBitmap(Y)) !== null && W !== void 0 ? W : e0({
        type: L.type,
        length: Y,
        nullCount: Y,
        nullBitmap: new Uint8Array(N)
      });
  }
  return [
    Q.assign(K),
    e0({ type: new H6(K), length: Y, children: z })
  ];
}
function AD(Q, J, Y = /* @__PURE__ */ new Map) {
  for (let W = -1, K = Q.length;++W < K; ) {
    let N = Q[W].type, F = J[W];
    if (C0.isDictionary(N)) {
      if (!Y.has(N.id)) {
        if (F.dictionary)
          Y.set(N.id, F.dictionary);
      } else if (Y.get(N.id) !== F.dictionary)
        throw new Error("Cannot create Schema containing two different dictionaries with the same Id");
    }
    if (N.children && N.children.length > 0)
      AD(N.children, F.children, Y);
  }
  return Y;
}

class Pq extends z6 {
  constructor(Q) {
    let J = Q.fields.map((W) => e0({ type: W.type })), Y = e0({ type: new H6(Q.fields), nullCount: 0, children: J });
    super(Q, Y);
  }
}

// node_modules/apache-arrow/fb/body-compression-method.mjs
var p3;
(function(Q) {
  Q[Q.BUFFER = 0] = "BUFFER";
})(p3 || (p3 = {}));

// node_modules/apache-arrow/fb/compression-type.mjs
var d3;
(function(Q) {
  Q[Q.LZ4_FRAME = 0] = "LZ4_FRAME", Q[Q.ZSTD = 1] = "ZSTD";
})(d3 || (d3 = {}));

// node_modules/apache-arrow/fb/body-compression.mjs
class C4 {
  constructor() {
    this.bb = null, this.bb_pos = 0;
  }
  __init(Q, J) {
    return this.bb_pos = Q, this.bb = J, this;
  }
  static getRootAsBodyCompression(Q, J) {
    return (J || new C4).__init(Q.readInt32(Q.position()) + Q.position(), Q);
  }
  static getSizePrefixedRootAsBodyCompression(Q, J) {
    return Q.setPosition(Q.position() + R0), (J || new C4).__init(Q.readInt32(Q.position()) + Q.position(), Q);
  }
  codec() {
    let Q = this.bb.__offset(this.bb_pos, 4);
    return Q ? this.bb.readInt8(this.bb_pos + Q) : d3.LZ4_FRAME;
  }
  method() {
    let Q = this.bb.__offset(this.bb_pos, 6);
    return Q ? this.bb.readInt8(this.bb_pos + Q) : p3.BUFFER;
  }
  static startBodyCompression(Q) {
    Q.startObject(2);
  }
  static addCodec(Q, J) {
    Q.addFieldInt8(0, J, d3.LZ4_FRAME);
  }
  static addMethod(Q, J) {
    Q.addFieldInt8(1, J, p3.BUFFER);
  }
  static endBodyCompression(Q) {
    return Q.endObject();
  }
  static createBodyCompression(Q, J, Y) {
    return C4.startBodyCompression(Q), C4.addCodec(Q, J), C4.addMethod(Q, Y), C4.endBodyCompression(Q);
  }
}

// node_modules/apache-arrow/fb/buffer.mjs
class l3 {
  constructor() {
    this.bb = null, this.bb_pos = 0;
  }
  __init(Q, J) {
    return this.bb_pos = Q, this.bb = J, this;
  }
  offset() {
    return this.bb.readInt64(this.bb_pos);
  }
  length() {
    return this.bb.readInt64(this.bb_pos + 8);
  }
  static sizeOf() {
    return 16;
  }
  static createBuffer(Q, J, Y) {
    return Q.prep(8, 16), Q.writeInt64(Y), Q.writeInt64(J), Q.offset();
  }
}

// node_modules/apache-arrow/fb/field-node.mjs
class n3 {
  constructor() {
    this.bb = null, this.bb_pos = 0;
  }
  __init(Q, J) {
    return this.bb_pos = Q, this.bb = J, this;
  }
  length() {
    return this.bb.readInt64(this.bb_pos);
  }
  nullCount() {
    return this.bb.readInt64(this.bb_pos + 8);
  }
  static sizeOf() {
    return 16;
  }
  static createFieldNode(Q, J, Y) {
    return Q.prep(8, 16), Q.writeInt64(Y), Q.writeInt64(J), Q.offset();
  }
}

// node_modules/apache-arrow/fb/record-batch.mjs
class bQ {
  constructor() {
    this.bb = null, this.bb_pos = 0;
  }
  __init(Q, J) {
    return this.bb_pos = Q, this.bb = J, this;
  }
  static getRootAsRecordBatch(Q, J) {
    return (J || new bQ).__init(Q.readInt32(Q.position()) + Q.position(), Q);
  }
  static getSizePrefixedRootAsRecordBatch(Q, J) {
    return Q.setPosition(Q.position() + R0), (J || new bQ).__init(Q.readInt32(Q.position()) + Q.position(), Q);
  }
  length() {
    let Q = this.bb.__offset(this.bb_pos, 4);
    return Q ? this.bb.readInt64(this.bb_pos + Q) : this.bb.createLong(0, 0);
  }
  nodes(Q, J) {
    let Y = this.bb.__offset(this.bb_pos, 6);
    return Y ? (J || new n3).__init(this.bb.__vector(this.bb_pos + Y) + Q * 16, this.bb) : null;
  }
  nodesLength() {
    let Q = this.bb.__offset(this.bb_pos, 6);
    return Q ? this.bb.__vector_len(this.bb_pos + Q) : 0;
  }
  buffers(Q, J) {
    let Y = this.bb.__offset(this.bb_pos, 8);
    return Y ? (J || new l3).__init(this.bb.__vector(this.bb_pos + Y) + Q * 16, this.bb) : null;
  }
  buffersLength() {
    let Q = this.bb.__offset(this.bb_pos, 8);
    return Q ? this.bb.__vector_len(this.bb_pos + Q) : 0;
  }
  compression(Q) {
    let J = this.bb.__offset(this.bb_pos, 10);
    return J ? (Q || new C4).__init(this.bb.__indirect(this.bb_pos + J), this.bb) : null;
  }
  static startRecordBatch(Q) {
    Q.startObject(4);
  }
  static addLength(Q, J) {
    Q.addFieldInt64(0, J, Q.createLong(0, 0));
  }
  static addNodes(Q, J) {
    Q.addFieldOffset(1, J, 0);
  }
  static startNodesVector(Q, J) {
    Q.startVector(16, J, 8);
  }
  static addBuffers(Q, J) {
    Q.addFieldOffset(2, J, 0);
  }
  static startBuffersVector(Q, J) {
    Q.startVector(16, J, 8);
  }
  static addCompression(Q, J) {
    Q.addFieldOffset(3, J, 0);
  }
  static endRecordBatch(Q) {
    return Q.endObject();
  }
}

// node_modules/apache-arrow/fb/dictionary-batch.mjs
class dX {
  constructor() {
    this.bb = null, this.bb_pos = 0;
  }
  __init(Q, J) {
    return this.bb_pos = Q, this.bb = J, this;
  }
  static getRootAsDictionaryBatch(Q, J) {
    return (J || new dX).__init(Q.readInt32(Q.position()) + Q.position(), Q);
  }
  static getSizePrefixedRootAsDictionaryBatch(Q, J) {
    return Q.setPosition(Q.position() + R0), (J || new dX).__init(Q.readInt32(Q.position()) + Q.position(), Q);
  }
  id() {
    let Q = this.bb.__offset(this.bb_pos, 4);
    return Q ? this.bb.readInt64(this.bb_pos + Q) : this.bb.createLong(0, 0);
  }
  data(Q) {
    let J = this.bb.__offset(this.bb_pos, 6);
    return J ? (Q || new bQ).__init(this.bb.__indirect(this.bb_pos + J), this.bb) : null;
  }
  isDelta() {
    let Q = this.bb.__offset(this.bb_pos, 8);
    return Q ? !!this.bb.readInt8(this.bb_pos + Q) : !1;
  }
  static startDictionaryBatch(Q) {
    Q.startObject(3);
  }
  static addId(Q, J) {
    Q.addFieldInt64(0, J, Q.createLong(0, 0));
  }
  static addData(Q, J) {
    Q.addFieldOffset(1, J, 0);
  }
  static addIsDelta(Q, J) {
    Q.addFieldInt8(2, +J, 0);
  }
  static endDictionaryBatch(Q) {
    return Q.endObject();
  }
}

// node_modules/apache-arrow/fb/message-header.mjs
var Aq;
(function(Q) {
  Q[Q.NONE = 0] = "NONE", Q[Q.Schema = 1] = "Schema", Q[Q.DictionaryBatch = 2] = "DictionaryBatch", Q[Q.RecordBatch = 3] = "RecordBatch", Q[Q.Tensor = 4] = "Tensor", Q[Q.SparseTensor = 5] = "SparseTensor";
})(Aq || (Aq = {}));

// node_modules/apache-arrow/fb/message.mjs
class $8 {
  constructor() {
    this.bb = null, this.bb_pos = 0;
  }
  __init(Q, J) {
    return this.bb_pos = Q, this.bb = J, this;
  }
  static getRootAsMessage(Q, J) {
    return (J || new $8).__init(Q.readInt32(Q.position()) + Q.position(), Q);
  }
  static getSizePrefixedRootAsMessage(Q, J) {
    return Q.setPosition(Q.position() + R0), (J || new $8).__init(Q.readInt32(Q.position()) + Q.position(), Q);
  }
  version() {
    let Q = this.bb.__offset(this.bb_pos, 4);
    return Q ? this.bb.readInt16(this.bb_pos + Q) : MJ.V1;
  }
  headerType() {
    let Q = this.bb.__offset(this.bb_pos, 6);
    return Q ? this.bb.readUint8(this.bb_pos + Q) : Aq.NONE;
  }
  header(Q) {
    let J = this.bb.__offset(this.bb_pos, 8);
    return J ? this.bb.__union(Q, this.bb_pos + J) : null;
  }
  bodyLength() {
    let Q = this.bb.__offset(this.bb_pos, 10);
    return Q ? this.bb.readInt64(this.bb_pos + Q) : this.bb.createLong(0, 0);
  }
  customMetadata(Q, J) {
    let Y = this.bb.__offset(this.bb_pos, 12);
    return Y ? (J || new P6).__init(this.bb.__indirect(this.bb.__vector(this.bb_pos + Y) + Q * 4), this.bb) : null;
  }
  customMetadataLength() {
    let Q = this.bb.__offset(this.bb_pos, 12);
    return Q ? this.bb.__vector_len(this.bb_pos + Q) : 0;
  }
  static startMessage(Q) {
    Q.startObject(5);
  }
  static addVersion(Q, J) {
    Q.addFieldInt16(0, J, MJ.V1);
  }
  static addHeaderType(Q, J) {
    Q.addFieldInt8(1, J, Aq.NONE);
  }
  static addHeader(Q, J) {
    Q.addFieldOffset(2, J, 0);
  }
  static addBodyLength(Q, J) {
    Q.addFieldInt64(3, J, Q.createLong(0, 0));
  }
  static addCustomMetadata(Q, J) {
    Q.addFieldOffset(4, J, 0);
  }
  static createCustomMetadataVector(Q, J) {
    Q.startVector(4, J.length, 4);
    for (let Y = J.length - 1;Y >= 0; Y--)
      Q.addOffset(J[Y]);
    return Q.endVector();
  }
  static startCustomMetadataVector(Q, J) {
    Q.startVector(4, J, 4);
  }
  static endMessage(Q) {
    return Q.endObject();
  }
  static finishMessageBuffer(Q, J) {
    Q.finish(J);
  }
  static finishSizePrefixedMessageBuffer(Q, J) {
    Q.finish(J, void 0, !0);
  }
  static createMessage(Q, J, Y, W, K, z) {
    return $8.startMessage(Q), $8.addVersion(Q, J), $8.addHeaderType(Q, Y), $8.addHeader(Q, W), $8.addBodyLength(Q, K), $8.addCustomMetadata(Q, z), $8.endMessage(Q);
  }
}

// node_modules/apache-arrow/visitor/typeassembler.mjs
var mh = L8;

class LD extends y0 {
  visit(Q, J) {
    return Q == null || J == null ? void 0 : super.visit(Q, J);
  }
  visitNull(Q, J) {
    return CJ.startNull(J), CJ.endNull(J);
  }
  visitInt(Q, J) {
    return QQ.startInt(J), QQ.addBitWidth(J, Q.bitWidth), QQ.addIsSigned(J, Q.isSigned), QQ.endInt(J);
  }
  visitFloat(Q, J) {
    return CZ.startFloatingPoint(J), CZ.addPrecision(J, Q.precision), CZ.endFloatingPoint(J);
  }
  visitBinary(Q, J) {
    return kJ.startBinary(J), kJ.endBinary(J);
  }
  visitBool(Q, J) {
    return RJ.startBool(J), RJ.endBool(J);
  }
  visitUtf8(Q, J) {
    return SJ.startUtf8(J), SJ.endUtf8(J);
  }
  visitDecimal(Q, J) {
    return ZQ.startDecimal(J), ZQ.addScale(J, Q.scale), ZQ.addPrecision(J, Q.precision), ZQ.addBitWidth(J, Q.bitWidth), ZQ.endDecimal(J);
  }
  visitDate(Q, J) {
    return RZ.startDate(J), RZ.addUnit(J, Q.unit), RZ.endDate(J);
  }
  visitTime(Q, J) {
    return hQ.startTime(J), hQ.addUnit(J, Q.unit), hQ.addBitWidth(J, Q.bitWidth), hQ.endTime(J);
  }
  visitTimestamp(Q, J) {
    let Y = Q.timezone && J.createString(Q.timezone) || void 0;
    if (yQ.startTimestamp(J), yQ.addUnit(J, Q.unit), Y !== void 0)
      yQ.addTimezone(J, Y);
    return yQ.endTimestamp(J);
  }
  visitInterval(Q, J) {
    return VZ.startInterval(J), VZ.addUnit(J, Q.unit), VZ.endInterval(J);
  }
  visitList(Q, J) {
    return BJ.startList(J), BJ.endList(J);
  }
  visitStruct(Q, J) {
    return VJ.startStruct_(J), VJ.endStruct_(J);
  }
  visitUnion(Q, J) {
    XQ.startTypeIdsVector(J, Q.typeIds.length);
    let Y = XQ.createTypeIdsVector(J, Q.typeIds);
    return XQ.startUnion(J), XQ.addMode(J, Q.mode), XQ.addTypeIds(J, Y), XQ.endUnion(J);
  }
  visitDictionary(Q, J) {
    let Y = this.visit(Q.indices, J);
    if (WX.startDictionaryEncoding(J), WX.addId(J, new mh(Q.id, 0)), WX.addIsOrdered(J, Q.isOrdered), Y !== void 0)
      WX.addIndexType(J, Y);
    return WX.endDictionaryEncoding(J);
  }
  visitFixedSizeBinary(Q, J) {
    return jZ.startFixedSizeBinary(J), jZ.addByteWidth(J, Q.byteWidth), jZ.endFixedSizeBinary(J);
  }
  visitFixedSizeList(Q, J) {
    return BZ.startFixedSizeList(J), BZ.addListSize(J, Q.listSize), BZ.endFixedSizeList(J);
  }
  visitMap(Q, J) {
    return SZ.startMap(J), SZ.addKeysSorted(J, Q.keysSorted), SZ.endMap(J);
  }
}
var _H = new LD;

// node_modules/apache-arrow/ipc/metadata/json.mjs
function DD(Q, J = /* @__PURE__ */ new Map) {
  return new w1(bh(Q, J), TH(Q.customMetadata), J);
}
function VE(Q) {
  return new $Q(Q.count, RD(Q.columns), jD(Q.columns));
}
function kD(Q) {
  return new KZ(VE(Q.data), Q.id, Q.isDelta);
}
function bh(Q, J) {
  return (Q.fields || []).filter(Boolean).map((Y) => q1.fromJSON(Y, J));
}
function OD(Q, J) {
  return (Q.children || []).filter(Boolean).map((Y) => q1.fromJSON(Y, J));
}
function RD(Q) {
  return (Q || []).reduce((J, Y) => [
    ...J,
    new lX(Y.count, uh(Y.VALIDITY)),
    ...RD(Y.children)
  ], []);
}
function jD(Q, J = []) {
  for (let Y = -1, W = (Q || []).length;++Y < W; ) {
    let K = Q[Y];
    K.VALIDITY && J.push(new WZ(J.length, K.VALIDITY.length)), K.TYPE && J.push(new WZ(J.length, K.TYPE.length)), K.OFFSET && J.push(new WZ(J.length, K.OFFSET.length)), K.DATA && J.push(new WZ(J.length, K.DATA.length)), J = jD(K.children, J);
  }
  return J;
}
function uh(Q) {
  return (Q || []).reduce((J, Y) => J + +(Y === 0), 0);
}
function BD(Q, J) {
  let Y, W, K, z, N, F;
  if (!J || !(z = Q.dictionary))
    N = MD(Q, OD(Q, J)), K = new q1(Q.name, N, Q.nullable, TH(Q.customMetadata));
  else if (!J.has(Y = z.id))
    W = (W = z.indexType) ? wD(W) : new L4, J.set(Y, N = MD(Q, OD(Q, J))), F = new MZ(N, W, Y, z.isOrdered), K = new q1(Q.name, F, Q.nullable, TH(Q.customMetadata));
  else
    W = (W = z.indexType) ? wD(W) : new L4, F = new MZ(J.get(Y), W, Y, z.isOrdered), K = new q1(Q.name, F, Q.nullable, TH(Q.customMetadata));
  return K || null;
}
function TH(Q) {
  return new Map(Object.entries(Q || {}));
}
function wD(Q) {
  return new u6(Q.isSigned, Q.bitWidth);
}
function MD(Q, J) {
  let Y = Q.type.name;
  switch (Y) {
    case "NONE":
      return new vQ;
    case "null":
      return new vQ;
    case "binary":
      return new HJ;
    case "utf8":
      return new GJ;
    case "bool":
      return new zJ;
    case "list":
      return new fX((J || [])[0]);
    case "struct":
      return new H6(J || []);
    case "struct_":
      return new H6(J || []);
  }
  switch (Y) {
    case "int": {
      let W = Q.type;
      return new u6(W.isSigned, W.bitWidth);
    }
    case "floatingpoint": {
      let W = Q.type;
      return new XZ(K6[W.precision]);
    }
    case "decimal": {
      let W = Q.type;
      return new NJ(W.scale, W.precision, W.bitWidth);
    }
    case "date": {
      let W = Q.type;
      return new EJ(f8[W.unit]);
    }
    case "time": {
      let W = Q.type;
      return new yX(F1[W.unit], W.bitWidth);
    }
    case "timestamp": {
      let W = Q.type;
      return new FJ(F1[W.unit], W.timezone);
    }
    case "interval": {
      let W = Q.type;
      return new UJ(wQ[W.unit]);
    }
    case "union": {
      let W = Q.type;
      return new mX(k6[W.mode], W.typeIds || [], J || []);
    }
    case "fixedsizebinary": {
      let W = Q.type;
      return new PJ(W.byteWidth);
    }
    case "fixedsizelist": {
      let W = Q.type;
      return new bX(W.listSize, (J || [])[0]);
    }
    case "map": {
      let W = Q.type;
      return new uX((J || [])[0], W.keysSorted);
    }
  }
  throw new Error(`Unrecognized type: "${Y}"`);
}

// node_modules/apache-arrow/ipc/metadata/message.mjs
var T$ = L8, ch = V$, ph = qZ;

class w8 {
  constructor(Q, J, Y, W) {
    this._version = J, this._headerType = Y, this.body = new Uint8Array(0), W && (this._createHeader = () => W), this._bodyLength = typeof Q === "number" ? Q : Q.low;
  }
  static fromJSON(Q, J) {
    let Y = new w8(0, A8.V4, J);
    return Y._createHeader = dh(Q, J), Y;
  }
  static decode(Q) {
    Q = new ph(n0(Q));
    let J = $8.getRootAsMessage(Q), Y = J.bodyLength(), W = J.version(), K = J.headerType(), z = new w8(Y, W, K);
    return z._createHeader = lh(J, K), z;
  }
  static encode(Q) {
    let J = new ch, Y = -1;
    if (Q.isSchema())
      Y = w1.encode(J, Q.header());
    else if (Q.isRecordBatch())
      Y = $Q.encode(J, Q.header());
    else if (Q.isDictionaryBatch())
      Y = KZ.encode(J, Q.header());
    return $8.startMessage(J), $8.addVersion(J, A8.V4), $8.addHeader(J, Y), $8.addHeaderType(J, Q.headerType), $8.addBodyLength(J, new T$(Q.bodyLength, 0)), $8.finishMessageBuffer(J, $8.endMessage(J)), J.asUint8Array();
  }
  static from(Q, J = 0) {
    if (Q instanceof w1)
      return new w8(0, A8.V4, B1.Schema, Q);
    if (Q instanceof $Q)
      return new w8(J, A8.V4, B1.RecordBatch, Q);
    if (Q instanceof KZ)
      return new w8(J, A8.V4, B1.DictionaryBatch, Q);
    throw new Error(`Unrecognized Message header: ${Q}`);
  }
  get type() {
    return this.headerType;
  }
  get version() {
    return this._version;
  }
  get headerType() {
    return this._headerType;
  }
  get bodyLength() {
    return this._bodyLength;
  }
  header() {
    return this._createHeader();
  }
  isSchema() {
    return this.headerType === B1.Schema;
  }
  isRecordBatch() {
    return this.headerType === B1.RecordBatch;
  }
  isDictionaryBatch() {
    return this.headerType === B1.DictionaryBatch;
  }
}

class $Q {
  constructor(Q, J, Y) {
    this._nodes = J, this._buffers = Y, this._length = typeof Q === "number" ? Q : Q.low;
  }
  get nodes() {
    return this._nodes;
  }
  get length() {
    return this._length;
  }
  get buffers() {
    return this._buffers;
  }
}

class KZ {
  constructor(Q, J, Y = !1) {
    this._data = Q, this._isDelta = Y, this._id = typeof J === "number" ? J : J.low;
  }
  get id() {
    return this._id;
  }
  get data() {
    return this._data;
  }
  get isDelta() {
    return this._isDelta;
  }
  get length() {
    return this.data.length;
  }
  get nodes() {
    return this.data.nodes;
  }
  get buffers() {
    return this.data.buffers;
  }
}

class WZ {
  constructor(Q, J) {
    this.offset = typeof Q === "number" ? Q : Q.low, this.length = typeof J === "number" ? J : J.low;
  }
}

class lX {
  constructor(Q, J) {
    this.length = typeof Q === "number" ? Q : Q.low, this.nullCount = typeof J === "number" ? J : J.low;
  }
}
function dh(Q, J) {
  return () => {
    switch (J) {
      case B1.Schema:
        return w1.fromJSON(Q);
      case B1.RecordBatch:
        return $Q.fromJSON(Q);
      case B1.DictionaryBatch:
        return KZ.fromJSON(Q);
    }
    throw new Error(`Unrecognized Message type: { name: ${B1[J]}, type: ${J} }`);
  };
}
function lh(Q, J) {
  return () => {
    switch (J) {
      case B1.Schema:
        return w1.decode(Q.header(new I6));
      case B1.RecordBatch:
        return $Q.decode(Q.header(new bQ), Q.version());
      case B1.DictionaryBatch:
        return KZ.decode(Q.header(new dX), Q.version());
    }
    throw new Error(`Unrecognized Message type: { name: ${B1[J]}, type: ${J} }`);
  };
}
q1.encode = Xy;
q1.decode = Qy;
q1.fromJSON = BD;
w1.encode = Zy;
w1.decode = nh;
w1.fromJSON = DD;
$Q.encode = Jy;
$Q.decode = sh;
$Q.fromJSON = VE;
KZ.encode = $y;
KZ.decode = oh;
KZ.fromJSON = kD;
lX.encode = Yy;
lX.decode = rh;
WZ.encode = qy;
WZ.decode = ah;
function nh(Q, J = /* @__PURE__ */ new Map) {
  let Y = eh(Q, J);
  return new w1(Y, gH(Q), J);
}
function sh(Q, J = A8.V4) {
  if (Q.compression() !== null)
    throw new Error("Record batch compression not implemented");
  return new $Q(Q.length(), ih(Q), th(Q, J));
}
function oh(Q, J = A8.V4) {
  return new KZ($Q.decode(Q.data(), J), Q.id(), Q.isDelta());
}
function ah(Q) {
  return new WZ(Q.offset(), Q.length());
}
function rh(Q) {
  return new lX(Q.length(), Q.nullCount());
}
function ih(Q) {
  let J = [];
  for (let Y, W = -1, K = -1, z = Q.nodesLength();++W < z; )
    if (Y = Q.nodes(W))
      J[++K] = lX.decode(Y);
  return J;
}
function th(Q, J) {
  let Y = [];
  for (let W, K = -1, z = -1, N = Q.buffersLength();++K < N; )
    if (W = Q.buffers(K)) {
      if (J < A8.V4)
        W.bb_pos += 8 * (K + 1);
      Y[++z] = WZ.decode(W);
    }
  return Y;
}
function eh(Q, J) {
  let Y = [];
  for (let W, K = -1, z = -1, N = Q.fieldsLength();++K < N; )
    if (W = Q.fields(K))
      Y[++z] = q1.decode(W, J);
  return Y;
}
function CD(Q, J) {
  let Y = [];
  for (let W, K = -1, z = -1, N = Q.childrenLength();++K < N; )
    if (W = Q.children(K))
      Y[++z] = q1.decode(W, J);
  return Y;
}
function Qy(Q, J) {
  let Y, W, K, z, N, F;
  if (!J || !(F = Q.dictionary()))
    K = SD(Q, CD(Q, J)), W = new q1(Q.name(), K, Q.nullable(), gH(Q));
  else if (!J.has(Y = F.id().low))
    z = (z = F.indexType()) ? VD(z) : new L4, J.set(Y, K = SD(Q, CD(Q, J))), N = new MZ(K, z, Y, F.isOrdered()), W = new q1(Q.name(), N, Q.nullable(), gH(Q));
  else
    z = (z = F.indexType()) ? VD(z) : new L4, N = new MZ(J.get(Y), z, Y, F.isOrdered()), W = new q1(Q.name(), N, Q.nullable(), gH(Q));
  return W || null;
}
function gH(Q) {
  let J = /* @__PURE__ */ new Map;
  if (Q) {
    for (let Y, W, K = -1, z = Math.trunc(Q.customMetadataLength());++K < z; )
      if ((Y = Q.customMetadata(K)) && (W = Y.key()) != null)
        J.set(W, Y.value());
  }
  return J;
}
function VD(Q) {
  return new u6(Q.isSigned(), Q.bitWidth());
}
function SD(Q, J) {
  let Y = Q.typeType();
  switch (Y) {
    case G6.NONE:
      return new vQ;
    case G6.Null:
      return new vQ;
    case G6.Binary:
      return new HJ;
    case G6.Utf8:
      return new GJ;
    case G6.Bool:
      return new zJ;
    case G6.List:
      return new fX((J || [])[0]);
    case G6.Struct_:
      return new H6(J || []);
  }
  switch (Y) {
    case G6.Int: {
      let W = Q.type(new QQ);
      return new u6(W.isSigned(), W.bitWidth());
    }
    case G6.FloatingPoint: {
      let W = Q.type(new CZ);
      return new XZ(W.precision());
    }
    case G6.Decimal: {
      let W = Q.type(new ZQ);
      return new NJ(W.scale(), W.precision(), W.bitWidth());
    }
    case G6.Date: {
      let W = Q.type(new RZ);
      return new EJ(W.unit());
    }
    case G6.Time: {
      let W = Q.type(new hQ);
      return new yX(W.unit(), W.bitWidth());
    }
    case G6.Timestamp: {
      let W = Q.type(new yQ);
      return new FJ(W.unit(), W.timezone());
    }
    case G6.Interval: {
      let W = Q.type(new VZ);
      return new UJ(W.unit());
    }
    case G6.Union: {
      let W = Q.type(new XQ);
      return new mX(W.mode(), W.typeIdsArray() || [], J || []);
    }
    case G6.FixedSizeBinary: {
      let W = Q.type(new jZ);
      return new PJ(W.byteWidth());
    }
    case G6.FixedSizeList: {
      let W = Q.type(new BZ);
      return new bX(W.listSize(), (J || [])[0]);
    }
    case G6.Map: {
      let W = Q.type(new SZ);
      return new uX((J || [])[0], W.keysSorted());
    }
  }
  throw new Error(`Unrecognized type: "${G6[Y]}" (${Y})`);
}
function Zy(Q, J) {
  let Y = J.fields.map((z) => q1.encode(Q, z));
  I6.startFieldsVector(Q, Y.length);
  let W = I6.createFieldsVector(Q, Y), K = !(J.metadata && J.metadata.size > 0) ? -1 : I6.createCustomMetadataVector(Q, [...J.metadata].map(([z, N]) => {
    let F = Q.createString(`${z}`), L = Q.createString(`${N}`);
    return P6.startKeyValue(Q), P6.addKey(Q, F), P6.addValue(Q, L), P6.endKeyValue(Q);
  }));
  if (I6.startSchema(Q), I6.addFields(Q, W), I6.addEndianness(Q, Wy ? DJ.Little : DJ.Big), K !== -1)
    I6.addCustomMetadata(Q, K);
  return I6.endSchema(Q);
}
function Xy(Q, J) {
  let Y = -1, W = -1, K = -1, z = J.type, N = J.typeId;
  if (!C0.isDictionary(z))
    W = _H.visit(z, Q);
  else
    N = z.dictionary.typeId, K = _H.visit(z, Q), W = _H.visit(z.dictionary, Q);
  let F = (z.children || []).map((D) => q1.encode(Q, D)), L = O8.createChildrenVector(Q, F), w = !(J.metadata && J.metadata.size > 0) ? -1 : O8.createCustomMetadataVector(Q, [...J.metadata].map(([D, R]) => {
    let V = Q.createString(`${D}`), g = Q.createString(`${R}`);
    return P6.startKeyValue(Q), P6.addKey(Q, V), P6.addValue(Q, g), P6.endKeyValue(Q);
  }));
  if (J.name)
    Y = Q.createString(J.name);
  if (O8.startField(Q), O8.addType(Q, W), O8.addTypeType(Q, N), O8.addChildren(Q, L), O8.addNullable(Q, !!J.nullable), Y !== -1)
    O8.addName(Q, Y);
  if (K !== -1)
    O8.addDictionary(Q, K);
  if (w !== -1)
    O8.addCustomMetadata(Q, w);
  return O8.endField(Q);
}
function Jy(Q, J) {
  let Y = J.nodes || [], W = J.buffers || [];
  bQ.startNodesVector(Q, Y.length);
  for (let N of Y.slice().reverse())
    lX.encode(Q, N);
  let K = Q.endVector();
  bQ.startBuffersVector(Q, W.length);
  for (let N of W.slice().reverse())
    WZ.encode(Q, N);
  let z = Q.endVector();
  return bQ.startRecordBatch(Q), bQ.addLength(Q, new T$(J.length, 0)), bQ.addNodes(Q, K), bQ.addBuffers(Q, z), bQ.endRecordBatch(Q);
}
function $y(Q, J) {
  let Y = $Q.encode(Q, J.data);
  return dX.startDictionaryBatch(Q), dX.addId(Q, new T$(J.id, 0)), dX.addIsDelta(Q, J.isDelta), dX.addData(Q, Y), dX.endDictionaryBatch(Q);
}
function Yy(Q, J) {
  return n3.createFieldNode(Q, new T$(J.length, 0), new T$(J.nullCount, 0));
}
function qy(Q, J) {
  return l3.createBuffer(Q, new T$(J.offset, 0), new T$(J.length, 0));
}
var Wy = (() => {
  let Q = new ArrayBuffer(2);
  return new DataView(Q).setInt16(0, 256, !0), new Int16Array(Q)[0] === 256;
})();

// node_modules/apache-arrow/ipc/message.mjs
var IE = (Q) => `Expected ${B1[Q]} Message in stream, but was null or length 0.`, _E = (Q) => `Header pointer of flatbuffer-encoded ${B1[Q]} Message is null or length 0.`, ID = (Q, J) => `Expected to read ${Q} metadata bytes, but only read ${J}.`, _D = (Q, J) => `Expected to read ${Q} bytes for message body, but only read ${J}.`;

class s3 {
  constructor(Q) {
    this.source = Q instanceof j4 ? Q : new j4(Q);
  }
  [Symbol.iterator]() {
    return this;
  }
  next() {
    let Q;
    if ((Q = this.readMetadataLength()).done)
      return Y6;
    if (Q.value === -1 && (Q = this.readMetadataLength()).done)
      return Y6;
    if ((Q = this.readMetadata(Q.value)).done)
      return Y6;
    return Q;
  }
  throw(Q) {
    return this.source.throw(Q);
  }
  return(Q) {
    return this.source.return(Q);
  }
  readMessage(Q) {
    let J;
    if ((J = this.next()).done)
      return null;
    if (Q != null && J.value.headerType !== Q)
      throw new Error(IE(Q));
    return J.value;
  }
  readMessageBody(Q) {
    if (Q <= 0)
      return new Uint8Array(0);
    let J = n0(this.source.read(Q));
    if (J.byteLength < Q)
      throw new Error(_D(Q, J.byteLength));
    return J.byteOffset % 8 === 0 && J.byteOffset + J.byteLength <= J.buffer.byteLength ? J : J.slice();
  }
  readSchema(Q = !1) {
    let J = B1.Schema, Y = this.readMessage(J), W = Y === null || Y === void 0 ? void 0 : Y.header();
    if (Q && !W)
      throw new Error(_E(J));
    return W;
  }
  readMetadataLength() {
    let Q = this.source.read(hH), J = Q && new qZ(Q), Y = (J === null || J === void 0 ? void 0 : J.readInt32(0)) || 0;
    return { done: Y === 0, value: Y };
  }
  readMetadata(Q) {
    let J = this.source.read(Q);
    if (!J)
      return Y6;
    if (J.byteLength < Q)
      throw new Error(ID(Q, J.byteLength));
    return { done: !1, value: w8.decode(J) };
  }
}

class xH {
  constructor(Q, J) {
    this.source = Q instanceof IZ ? Q : T5(Q) ? new S$(Q, J) : new IZ(Q);
  }
  [Symbol.asyncIterator]() {
    return this;
  }
  next() {
    return U0(this, void 0, void 0, function* () {
      let Q;
      if ((Q = yield this.readMetadataLength()).done)
        return Y6;
      if (Q.value === -1 && (Q = yield this.readMetadataLength()).done)
        return Y6;
      if ((Q = yield this.readMetadata(Q.value)).done)
        return Y6;
      return Q;
    });
  }
  throw(Q) {
    return U0(this, void 0, void 0, function* () {
      return yield this.source.throw(Q);
    });
  }
  return(Q) {
    return U0(this, void 0, void 0, function* () {
      return yield this.source.return(Q);
    });
  }
  readMessage(Q) {
    return U0(this, void 0, void 0, function* () {
      let J;
      if ((J = yield this.next()).done)
        return null;
      if (Q != null && J.value.headerType !== Q)
        throw new Error(IE(Q));
      return J.value;
    });
  }
  readMessageBody(Q) {
    return U0(this, void 0, void 0, function* () {
      if (Q <= 0)
        return new Uint8Array(0);
      let J = n0(yield this.source.read(Q));
      if (J.byteLength < Q)
        throw new Error(_D(Q, J.byteLength));
      return J.byteOffset % 8 === 0 && J.byteOffset + J.byteLength <= J.buffer.byteLength ? J : J.slice();
    });
  }
  readSchema(Q = !1) {
    return U0(this, void 0, void 0, function* () {
      let J = B1.Schema, Y = yield this.readMessage(J), W = Y === null || Y === void 0 ? void 0 : Y.header();
      if (Q && !W)
        throw new Error(_E(J));
      return W;
    });
  }
  readMetadataLength() {
    return U0(this, void 0, void 0, function* () {
      let Q = yield this.source.read(hH), J = Q && new qZ(Q), Y = (J === null || J === void 0 ? void 0 : J.readInt32(0)) || 0;
      return { done: Y === 0, value: Y };
    });
  }
  readMetadata(Q) {
    return U0(this, void 0, void 0, function* () {
      let J = yield this.source.read(Q);
      if (!J)
        return Y6;
      if (J.byteLength < Q)
        throw new Error(ID(Q, J.byteLength));
      return { done: !1, value: w8.decode(J) };
    });
  }
}

class vH extends s3 {
  constructor(Q) {
    super(new Uint8Array(0));
    this._schema = !1, this._body = [], this._batchIndex = 0, this._dictionaryIndex = 0, this._json = Q instanceof GH ? Q : new GH(Q);
  }
  next() {
    let { _json: Q } = this;
    if (!this._schema)
      return this._schema = !0, { done: !1, value: w8.fromJSON(Q.schema, B1.Schema) };
    if (this._dictionaryIndex < Q.dictionaries.length) {
      let J = Q.dictionaries[this._dictionaryIndex++];
      return this._body = J.data.columns, { done: !1, value: w8.fromJSON(J, B1.DictionaryBatch) };
    }
    if (this._batchIndex < Q.batches.length) {
      let J = Q.batches[this._batchIndex++];
      return this._body = J.columns, { done: !1, value: w8.fromJSON(J, B1.RecordBatch) };
    }
    return this._body = [], Y6;
  }
  readMessageBody(Q) {
    return J(this._body);
    function J(Y) {
      return (Y || []).reduce((W, K) => [
        ...W,
        ...K.VALIDITY && [K.VALIDITY] || [],
        ...K.TYPE && [K.TYPE] || [],
        ...K.OFFSET && [K.OFFSET] || [],
        ...K.DATA && [K.DATA] || [],
        ...J(K.children)
      ], []);
    }
  }
  readMessage(Q) {
    let J;
    if ((J = this.next()).done)
      return null;
    if (Q != null && J.value.headerType !== Q)
      throw new Error(IE(Q));
    return J.value;
  }
  readSchema() {
    let Q = B1.Schema, J = this.readMessage(Q), Y = J === null || J === void 0 ? void 0 : J.header();
    if (!J || !Y)
      throw new Error(_E(Q));
    return Y;
  }
}
var hH = 4, SE = "ARROW1", Lq = new Uint8Array(SE.length);
for (let Q = 0;Q < SE.length; Q += 1)
  Lq[Q] = SE.codePointAt(Q);
function yH(Q, J = 0) {
  for (let Y = -1, W = Lq.length;++Y < W; )
    if (Lq[Y] !== Q[J + Y])
      return !1;
  return !0;
}
var Oq = Lq.length, TE = Oq + hH, TD = Oq * 2 + hH;

// node_modules/apache-arrow/ipc/reader.mjs
class MQ extends Gq {
  constructor(Q) {
    super();
    this._impl = Q;
  }
  get closed() {
    return this._impl.closed;
  }
  get schema() {
    return this._impl.schema;
  }
  get autoDestroy() {
    return this._impl.autoDestroy;
  }
  get dictionaries() {
    return this._impl.dictionaries;
  }
  get numDictionaries() {
    return this._impl.numDictionaries;
  }
  get numRecordBatches() {
    return this._impl.numRecordBatches;
  }
  get footer() {
    return this._impl.isFile() ? this._impl.footer : null;
  }
  isSync() {
    return this._impl.isSync();
  }
  isAsync() {
    return this._impl.isAsync();
  }
  isFile() {
    return this._impl.isFile();
  }
  isStream() {
    return this._impl.isStream();
  }
  next() {
    return this._impl.next();
  }
  throw(Q) {
    return this._impl.throw(Q);
  }
  return(Q) {
    return this._impl.return(Q);
  }
  cancel() {
    return this._impl.cancel();
  }
  reset(Q) {
    return this._impl.reset(Q), this._DOMStream = void 0, this._nodeStream = void 0, this;
  }
  open(Q) {
    let J = this._impl.open(Q);
    return QZ(J) ? J.then(() => this) : this;
  }
  readRecordBatch(Q) {
    return this._impl.isFile() ? this._impl.readRecordBatch(Q) : null;
  }
  [Symbol.iterator]() {
    return this._impl[Symbol.iterator]();
  }
  [Symbol.asyncIterator]() {
    return this._impl[Symbol.asyncIterator]();
  }
  toDOMStream() {
    return y8.toDOMStream(this.isSync() ? { [Symbol.iterator]: () => this } : { [Symbol.asyncIterator]: () => this });
  }
  toNodeStream() {
    return y8.toNodeStream(this.isSync() ? { [Symbol.iterator]: () => this } : { [Symbol.asyncIterator]: () => this }, { objectMode: !0 });
  }
  static throughNode(Q) {
    throw new Error('"throughNode" not available in this environment');
  }
  static throughDOM(Q, J) {
    throw new Error('"throughDOM" not available in this environment');
  }
  static from(Q) {
    if (Q instanceof MQ)
      return Q;
    else if (I5(Q))
      return Hy(Q);
    else if (T5(Q))
      return Ny(Q);
    else if (QZ(Q))
      return (() => U0(this, void 0, void 0, function* () {
        return yield MQ.from(yield Q);
      }))();
    else if (g5(Q) || w3(Q) || v5(Q) || OZ(Q))
      return zy(new IZ(Q));
    return Gy(new j4(Q));
  }
  static readAll(Q) {
    if (Q instanceof MQ)
      return Q.isSync() ? gD(Q) : xD(Q);
    else if (I5(Q) || ArrayBuffer.isView(Q) || XX(Q) || _5(Q))
      return gD(Q);
    return xD(Q);
  }
}

class xJ extends MQ {
  constructor(Q) {
    super(Q);
    this._impl = Q;
  }
  readAll() {
    return [...this];
  }
  [Symbol.iterator]() {
    return this._impl[Symbol.iterator]();
  }
  [Symbol.asyncIterator]() {
    return eQ(this, arguments, function* Q() {
      yield i0(yield* iY(ZX(this[Symbol.iterator]())));
    });
  }
}

class wq extends MQ {
  constructor(Q) {
    super(Q);
    this._impl = Q;
  }
  readAll() {
    var Q, J;
    return U0(this, void 0, void 0, function* () {
      let Y = new Array;
      try {
        for (var W = ZX(this), K;K = yield W.next(), !K.done; ) {
          let z = K.value;
          Y.push(z);
        }
      } catch (z) {
        Q = { error: z };
      } finally {
        try {
          if (K && !K.done && (J = W.return))
            yield J.call(W);
        } finally {
          if (Q)
            throw Q.error;
        }
      }
      return Y;
    });
  }
  [Symbol.iterator]() {
    throw new Error("AsyncRecordBatchStreamReader is not Iterable");
  }
  [Symbol.asyncIterator]() {
    return this._impl[Symbol.asyncIterator]();
  }
}

class Mq extends xJ {
  constructor(Q) {
    super(Q);
    this._impl = Q;
  }
}

class gE extends wq {
  constructor(Q) {
    super(Q);
    this._impl = Q;
  }
}

class xE {
  constructor(Q = /* @__PURE__ */ new Map) {
    this.closed = !1, this.autoDestroy = !0, this._dictionaryIndex = 0, this._recordBatchIndex = 0, this.dictionaries = Q;
  }
  get numDictionaries() {
    return this._dictionaryIndex;
  }
  get numRecordBatches() {
    return this._recordBatchIndex;
  }
  isSync() {
    return !1;
  }
  isAsync() {
    return !1;
  }
  isFile() {
    return !1;
  }
  isStream() {
    return !1;
  }
  reset(Q) {
    return this._dictionaryIndex = 0, this._recordBatchIndex = 0, this.schema = Q, this.dictionaries = /* @__PURE__ */ new Map, this;
  }
  _loadRecordBatch(Q, J) {
    let Y = this._loadVectors(Q, J, this.schema.fields), W = e0({ type: new H6(this.schema.fields), length: Q.length, children: Y });
    return new z6(this.schema, W);
  }
  _loadDictionaryBatch(Q, J) {
    let { id: Y, isDelta: W } = Q, { dictionaries: K, schema: z } = this, N = K.get(Y);
    if (W || !N) {
      let F = z.dictionaries.get(Y), L = this._loadVectors(Q.data, J, [F]);
      return (N && W ? N.concat(new Z1(L)) : new Z1(L)).memoize();
    }
    return N.memoize();
  }
  _loadVectors(Q, J, Y) {
    return new EH(J, Q.nodes, Q.buffers, this.dictionaries).visitMany(Y);
  }
}

class o3 extends xE {
  constructor(Q, J) {
    super(J);
    this._reader = !I5(Q) ? new s3(this._handle = Q) : new vH(this._handle = Q);
  }
  isSync() {
    return !0;
  }
  isStream() {
    return !0;
  }
  [Symbol.iterator]() {
    return this;
  }
  cancel() {
    if (!this.closed && (this.closed = !0))
      this.reset()._reader.return(), this._reader = null, this.dictionaries = null;
  }
  open(Q) {
    if (!this.closed) {
      if (this.autoDestroy = yD(this, Q), !(this.schema || (this.schema = this._reader.readSchema())))
        this.cancel();
    }
    return this;
  }
  throw(Q) {
    if (!this.closed && this.autoDestroy && (this.closed = !0))
      return this.reset()._reader.throw(Q);
    return Y6;
  }
  return(Q) {
    if (!this.closed && this.autoDestroy && (this.closed = !0))
      return this.reset()._reader.return(Q);
    return Y6;
  }
  next() {
    if (this.closed)
      return Y6;
    let Q, { _reader: J } = this;
    while (Q = this._readNextMessageAndValidate())
      if (Q.isSchema())
        this.reset(Q.header());
      else if (Q.isRecordBatch()) {
        this._recordBatchIndex++;
        let Y = Q.header(), W = J.readMessageBody(Q.bodyLength);
        return { done: !1, value: this._loadRecordBatch(Y, W) };
      } else if (Q.isDictionaryBatch()) {
        this._dictionaryIndex++;
        let Y = Q.header(), W = J.readMessageBody(Q.bodyLength), K = this._loadDictionaryBatch(Y, W);
        this.dictionaries.set(Y.id, K);
      }
    if (this.schema && this._recordBatchIndex === 0)
      return this._recordBatchIndex++, { done: !1, value: new Pq(this.schema) };
    return this.return();
  }
  _readNextMessageAndValidate(Q) {
    return this._reader.readMessage(Q);
  }
}

class a3 extends xE {
  constructor(Q, J) {
    super(J);
    this._reader = new xH(this._handle = Q);
  }
  isAsync() {
    return !0;
  }
  isStream() {
    return !0;
  }
  [Symbol.asyncIterator]() {
    return this;
  }
  cancel() {
    return U0(this, void 0, void 0, function* () {
      if (!this.closed && (this.closed = !0))
        yield this.reset()._reader.return(), this._reader = null, this.dictionaries = null;
    });
  }
  open(Q) {
    return U0(this, void 0, void 0, function* () {
      if (!this.closed) {
        if (this.autoDestroy = yD(this, Q), !(this.schema || (this.schema = yield this._reader.readSchema())))
          yield this.cancel();
      }
      return this;
    });
  }
  throw(Q) {
    return U0(this, void 0, void 0, function* () {
      if (!this.closed && this.autoDestroy && (this.closed = !0))
        return yield this.reset()._reader.throw(Q);
      return Y6;
    });
  }
  return(Q) {
    return U0(this, void 0, void 0, function* () {
      if (!this.closed && this.autoDestroy && (this.closed = !0))
        return yield this.reset()._reader.return(Q);
      return Y6;
    });
  }
  next() {
    return U0(this, void 0, void 0, function* () {
      if (this.closed)
        return Y6;
      let Q, { _reader: J } = this;
      while (Q = yield this._readNextMessageAndValidate())
        if (Q.isSchema())
          yield this.reset(Q.header());
        else if (Q.isRecordBatch()) {
          this._recordBatchIndex++;
          let Y = Q.header(), W = yield J.readMessageBody(Q.bodyLength);
          return { done: !1, value: this._loadRecordBatch(Y, W) };
        } else if (Q.isDictionaryBatch()) {
          this._dictionaryIndex++;
          let Y = Q.header(), W = yield J.readMessageBody(Q.bodyLength), K = this._loadDictionaryBatch(Y, W);
          this.dictionaries.set(Y.id, K);
        }
      if (this.schema && this._recordBatchIndex === 0)
        return this._recordBatchIndex++, { done: !1, value: new Pq(this.schema) };
      return yield this.return();
    });
  }
  _readNextMessageAndValidate(Q) {
    return U0(this, void 0, void 0, function* () {
      return yield this._reader.readMessage(Q);
    });
  }
}

class vE extends o3 {
  constructor(Q, J) {
    super(Q instanceof zH ? Q : new zH(Q), J);
  }
  get footer() {
    return this._footer;
  }
  get numDictionaries() {
    return this._footer ? this._footer.numDictionaries : 0;
  }
  get numRecordBatches() {
    return this._footer ? this._footer.numRecordBatches : 0;
  }
  isSync() {
    return !0;
  }
  isFile() {
    return !0;
  }
  open(Q) {
    if (!this.closed && !this._footer) {
      this.schema = (this._footer = this._readFooter()).schema;
      for (let J of this._footer.dictionaryBatches())
        J && this._readDictionaryBatch(this._dictionaryIndex++);
    }
    return super.open(Q);
  }
  readRecordBatch(Q) {
    var J;
    if (this.closed)
      return null;
    if (!this._footer)
      this.open();
    let Y = (J = this._footer) === null || J === void 0 ? void 0 : J.getRecordBatch(Q);
    if (Y && this._handle.seek(Y.offset)) {
      let W = this._reader.readMessage(B1.RecordBatch);
      if (W === null || W === void 0 ? void 0 : W.isRecordBatch()) {
        let K = W.header(), z = this._reader.readMessageBody(W.bodyLength);
        return this._loadRecordBatch(K, z);
      }
    }
    return null;
  }
  _readDictionaryBatch(Q) {
    var J;
    let Y = (J = this._footer) === null || J === void 0 ? void 0 : J.getDictionaryBatch(Q);
    if (Y && this._handle.seek(Y.offset)) {
      let W = this._reader.readMessage(B1.DictionaryBatch);
      if (W === null || W === void 0 ? void 0 : W.isDictionaryBatch()) {
        let K = W.header(), z = this._reader.readMessageBody(W.bodyLength), N = this._loadDictionaryBatch(K, z);
        this.dictionaries.set(K.id, N);
      }
    }
  }
  _readFooter() {
    let { _handle: Q } = this, J = Q.size - TE, Y = Q.readInt32(J), W = Q.readAt(J - Y, Y);
    return IJ.decode(W);
  }
  _readNextMessageAndValidate(Q) {
    var J;
    if (!this._footer)
      this.open();
    if (this._footer && this._recordBatchIndex < this.numRecordBatches) {
      let Y = (J = this._footer) === null || J === void 0 ? void 0 : J.getRecordBatch(this._recordBatchIndex);
      if (Y && this._handle.seek(Y.offset))
        return this._reader.readMessage(Q);
    }
    return null;
  }
}

class vD extends a3 {
  constructor(Q, ...J) {
    let Y = typeof J[0] !== "number" ? J.shift() : void 0, W = J[0] instanceof Map ? J.shift() : void 0;
    super(Q instanceof S$ ? Q : new S$(Q, Y), W);
  }
  get footer() {
    return this._footer;
  }
  get numDictionaries() {
    return this._footer ? this._footer.numDictionaries : 0;
  }
  get numRecordBatches() {
    return this._footer ? this._footer.numRecordBatches : 0;
  }
  isFile() {
    return !0;
  }
  isAsync() {
    return !0;
  }
  open(Q) {
    let J = Object.create(null, {
      open: { get: () => super.open }
    });
    return U0(this, void 0, void 0, function* () {
      if (!this.closed && !this._footer) {
        this.schema = (this._footer = yield this._readFooter()).schema;
        for (let Y of this._footer.dictionaryBatches())
          Y && (yield this._readDictionaryBatch(this._dictionaryIndex++));
      }
      return yield J.open.call(this, Q);
    });
  }
  readRecordBatch(Q) {
    var J;
    return U0(this, void 0, void 0, function* () {
      if (this.closed)
        return null;
      if (!this._footer)
        yield this.open();
      let Y = (J = this._footer) === null || J === void 0 ? void 0 : J.getRecordBatch(Q);
      if (Y && (yield this._handle.seek(Y.offset))) {
        let W = yield this._reader.readMessage(B1.RecordBatch);
        if (W === null || W === void 0 ? void 0 : W.isRecordBatch()) {
          let K = W.header(), z = yield this._reader.readMessageBody(W.bodyLength);
          return this._loadRecordBatch(K, z);
        }
      }
      return null;
    });
  }
  _readDictionaryBatch(Q) {
    var J;
    return U0(this, void 0, void 0, function* () {
      let Y = (J = this._footer) === null || J === void 0 ? void 0 : J.getDictionaryBatch(Q);
      if (Y && (yield this._handle.seek(Y.offset))) {
        let W = yield this._reader.readMessage(B1.DictionaryBatch);
        if (W === null || W === void 0 ? void 0 : W.isDictionaryBatch()) {
          let K = W.header(), z = yield this._reader.readMessageBody(W.bodyLength), N = this._loadDictionaryBatch(K, z);
          this.dictionaries.set(K.id, N);
        }
      }
    });
  }
  _readFooter() {
    return U0(this, void 0, void 0, function* () {
      let { _handle: Q } = this;
      Q._pending && (yield Q._pending);
      let J = Q.size - TE, Y = yield Q.readInt32(J), W = yield Q.readAt(J - Y, Y);
      return IJ.decode(W);
    });
  }
  _readNextMessageAndValidate(Q) {
    return U0(this, void 0, void 0, function* () {
      if (!this._footer)
        yield this.open();
      if (this._footer && this._recordBatchIndex < this.numRecordBatches) {
        let J = this._footer.getRecordBatch(this._recordBatchIndex);
        if (J && (yield this._handle.seek(J.offset)))
          return yield this._reader.readMessage(Q);
      }
      return null;
    });
  }
}

class hD extends o3 {
  constructor(Q, J) {
    super(Q, J);
  }
  _loadVectors(Q, J, Y) {
    return new $E(J, Q.nodes, Q.buffers, this.dictionaries).visitMany(Y);
  }
}
function yD(Q, J) {
  return J && typeof J.autoDestroy === "boolean" ? J.autoDestroy : Q.autoDestroy;
}
function* gD(Q) {
  let J = MQ.from(Q);
  try {
    if (!J.open({ autoDestroy: !1 }).closed)
      do
        yield J;
      while (!J.reset().open().closed);
  } finally {
    J.cancel();
  }
}
function xD(Q) {
  return eQ(this, arguments, function* J() {
    let Y = yield i0(MQ.from(Q));
    try {
      if (!(yield i0(Y.open({ autoDestroy: !1 }))).closed)
        do
          yield yield i0(Y);
        while (!(yield i0(Y.reset().open())).closed);
    } finally {
      yield i0(Y.cancel());
    }
  });
}
function Hy(Q) {
  return new xJ(new hD(Q));
}
function Gy(Q) {
  let J = Q.peek(Oq + 7 & -8);
  return J && J.byteLength >= 4 ? !yH(J) ? new xJ(new o3(Q)) : new Mq(new vE(Q.read())) : new xJ(new o3(function* () {}()));
}
function zy(Q) {
  return U0(this, void 0, void 0, function* () {
    let J = yield Q.peek(Oq + 7 & -8);
    return J && J.byteLength >= 4 ? !yH(J) ? new wq(new a3(Q)) : new Mq(new vE(yield Q.read())) : new wq(new a3(function() {
      return eQ(this, arguments, function* () {});
    }()));
  });
}
function Ny(Q) {
  return U0(this, void 0, void 0, function* () {
    let { size: J } = yield Q.stat(), Y = new S$(Q, J);
    if (J >= TD && yH(yield Y.readAt(0, Oq + 7 & -8)))
      return new gE(new vD(Y));
    return new wq(new a3(Y));
  });
}

// node_modules/apache-arrow/visitor/vectorassembler.mjs
class _6 extends y0 {
  constructor() {
    super();
    this._byteLength = 0, this._nodes = [], this._buffers = [], this._bufferRegions = [];
  }
  static assemble(...Q) {
    let J = (W) => W.flatMap((K) => Array.isArray(K) ? J(K) : K instanceof z6 ? K.data.children : K.data), Y = new _6;
    return Y.visitMany(J(Q)), Y;
  }
  visit(Q) {
    if (Q instanceof Z1)
      return this.visitMany(Q.data), this;
    let { type: J } = Q;
    if (!C0.isDictionary(J)) {
      let { length: Y, nullCount: W } = Q;
      if (Y > 2147483647)
        throw new RangeError("Cannot write arrays larger than 2^31 - 1 in length");
      if (!C0.isNull(J))
        HX.call(this, W <= 0 ? new Uint8Array(0) : Yq(Q.offset, Y, Q.nullBitmap));
      this.nodes.push(new lX(Y, W));
    }
    return super.visit(Q);
  }
  visitNull(Q) {
    return this;
  }
  visitDictionary(Q) {
    return this.visit(Q.clone(Q.type.indices));
  }
  get nodes() {
    return this._nodes;
  }
  get buffers() {
    return this._buffers;
  }
  get byteLength() {
    return this._byteLength;
  }
  get bufferRegions() {
    return this._bufferRegions;
  }
}
function HX(Q) {
  let J = Q.byteLength + 7 & -8;
  return this.buffers.push(Q), this.bufferRegions.push(new WZ(this._byteLength, J)), this._byteLength += J, this;
}
function Ey(Q) {
  let { type: J, length: Y, typeIds: W, valueOffsets: K } = Q;
  if (HX.call(this, W), J.mode === k6.Sparse)
    return hE.call(this, Q);
  else if (J.mode === k6.Dense)
    if (Q.offset <= 0)
      return HX.call(this, K), hE.call(this, Q);
    else {
      let z = W.reduce((D, R) => Math.max(D, R), W[0]), N = new Int32Array(z + 1), F = new Int32Array(z + 1).fill(-1), L = new Int32Array(Y), w = M3(-K[0], Y, K);
      for (let D, R, V = -1;++V < Y; ) {
        if ((R = F[D = W[V]]) === -1)
          R = F[D] = w[D];
        L[V] = w[V] - R, ++N[D];
      }
      HX.call(this, L);
      for (let D, R = -1, V = J.children.length;++R < V; )
        if (D = Q.children[R]) {
          let g = J.typeIds[R], s = Math.min(Y, N[g]);
          this.visit(D.slice(F[g], s));
        }
    }
  return this;
}
function Fy(Q) {
  let J;
  if (Q.nullCount >= Q.length)
    return HX.call(this, new Uint8Array(0));
  else if ((J = Q.values) instanceof Uint8Array)
    return HX.call(this, Yq(Q.offset, Q.length, J));
  return HX.call(this, j$(Q.values));
}
function vJ(Q) {
  return HX.call(this, Q.values.subarray(0, Q.length * Q.stride));
}
function fD(Q) {
  let { length: J, values: Y, valueOffsets: W } = Q, K = W[0], z = W[J], N = Math.min(z - K, Y.byteLength - K);
  return HX.call(this, M3(-W[0], J, W)), HX.call(this, Y.subarray(K, K + N)), this;
}
function yE(Q) {
  let { length: J, valueOffsets: Y } = Q;
  if (Y)
    HX.call(this, M3(Y[0], J, Y));
  return this.visit(Q.children[0]);
}
function hE(Q) {
  return this.visitMany(Q.type.children.map((J, Y) => Q.children[Y]).filter(Boolean))[0];
}
_6.prototype.visitBool = Fy;
_6.prototype.visitInt = vJ;
_6.prototype.visitFloat = vJ;
_6.prototype.visitUtf8 = fD;
_6.prototype.visitBinary = fD;
_6.prototype.visitFixedSizeBinary = vJ;
_6.prototype.visitDate = vJ;
_6.prototype.visitTimestamp = vJ;
_6.prototype.visitTime = vJ;
_6.prototype.visitDecimal = vJ;
_6.prototype.visitList = yE;
_6.prototype.visitStruct = hE;
_6.prototype.visitUnion = Ey;
_6.prototype.visitInterval = vJ;
_6.prototype.visitFixedSizeList = yE;
_6.prototype.visitMap = yE;

// node_modules/apache-arrow/ipc/writer.mjs
class Dq extends Gq {
  constructor(Q) {
    super();
    this._position = 0, this._started = !1, this._sink = new R4, this._schema = null, this._dictionaryBlocks = [], this._recordBatchBlocks = [], this._dictionaryDeltaOffsets = /* @__PURE__ */ new Map, OQ(Q) || (Q = { autoDestroy: !0, writeLegacyIpcFormat: !1 }), this._autoDestroy = typeof Q.autoDestroy === "boolean" ? Q.autoDestroy : !0, this._writeLegacyIpcFormat = typeof Q.writeLegacyIpcFormat === "boolean" ? Q.writeLegacyIpcFormat : !1;
  }
  static throughNode(Q) {
    throw new Error('"throughNode" not available in this environment');
  }
  static throughDOM(Q, J) {
    throw new Error('"throughDOM" not available in this environment');
  }
  toString(Q = !1) {
    return this._sink.toString(Q);
  }
  toUint8Array(Q = !1) {
    return this._sink.toUint8Array(Q);
  }
  writeAll(Q) {
    if (QZ(Q))
      return Q.then((J) => this.writeAll(J));
    else if (OZ(Q))
      return mE(this, Q);
    return fE(this, Q);
  }
  get closed() {
    return this._sink.closed;
  }
  [Symbol.asyncIterator]() {
    return this._sink[Symbol.asyncIterator]();
  }
  toDOMStream(Q) {
    return this._sink.toDOMStream(Q);
  }
  toNodeStream(Q) {
    return this._sink.toNodeStream(Q);
  }
  close() {
    return this.reset()._sink.close();
  }
  abort(Q) {
    return this.reset()._sink.abort(Q);
  }
  finish() {
    return this._autoDestroy ? this.close() : this.reset(this._sink, this._schema), this;
  }
  reset(Q = this._sink, J = null) {
    if (Q === this._sink || Q instanceof R4)
      this._sink = Q;
    else if (this._sink = new R4, Q && rw(Q))
      this.toDOMStream({ type: "bytes" }).pipeTo(Q);
    else if (Q && iw(Q))
      this.toNodeStream({ objectMode: !1 }).pipe(Q);
    if (this._started && this._schema)
      this._writeFooter(this._schema);
    if (this._started = !1, this._dictionaryBlocks = [], this._recordBatchBlocks = [], this._dictionaryDeltaOffsets = /* @__PURE__ */ new Map, !J || !_$(J, this._schema))
      if (J == null)
        this._position = 0, this._schema = null;
      else
        this._started = !0, this._schema = J, this._writeSchema(J);
    return this;
  }
  write(Q) {
    let J = null;
    if (!this._sink)
      throw new Error("RecordBatchWriter is closed");
    else if (Q == null)
      return this.finish() && void 0;
    else if (Q instanceof J8 && !(J = Q.schema))
      return this.finish() && void 0;
    else if (Q instanceof z6 && !(J = Q.schema))
      return this.finish() && void 0;
    if (J && !_$(J, this._schema)) {
      if (this._started && this._autoDestroy)
        return this.close();
      this.reset(this._sink, J);
    }
    if (Q instanceof z6) {
      if (!(Q instanceof Pq))
        this._writeRecordBatch(Q);
    } else if (Q instanceof J8)
      this.writeAll(Q.batches);
    else if (XX(Q))
      this.writeAll(Q);
  }
  _writeMessage(Q, J = 8) {
    let Y = J - 1, W = w8.encode(Q), K = W.byteLength, z = !this._writeLegacyIpcFormat ? 8 : 4, N = K + z + Y & ~Y, F = N - K - z;
    if (Q.headerType === B1.RecordBatch)
      this._recordBatchBlocks.push(new k4(N, Q.bodyLength, this._position));
    else if (Q.headerType === B1.DictionaryBatch)
      this._dictionaryBlocks.push(new k4(N, Q.bodyLength, this._position));
    if (!this._writeLegacyIpcFormat)
      this._write(Int32Array.of(-1));
    if (this._write(Int32Array.of(N - z)), K > 0)
      this._write(W);
    return this._writePadding(F);
  }
  _write(Q) {
    if (this._started) {
      let J = n0(Q);
      if (J && J.byteLength > 0)
        this._sink.write(J), this._position += J.byteLength;
    }
    return this;
  }
  _writeSchema(Q) {
    return this._writeMessage(w8.from(Q));
  }
  _writeFooter(Q) {
    return this._writeLegacyIpcFormat ? this._write(Int32Array.of(0)) : this._write(Int32Array.of(-1, 0));
  }
  _writeMagic() {
    return this._write(Lq);
  }
  _writePadding(Q) {
    return Q > 0 ? this._write(new Uint8Array(Q)) : this;
  }
  _writeRecordBatch(Q) {
    let { byteLength: J, nodes: Y, bufferRegions: W, buffers: K } = _6.assemble(Q), z = new $Q(Q.numRows, Y, W), N = w8.from(z, J);
    return this._writeDictionaries(Q)._writeMessage(N)._writeBodyBuffers(K);
  }
  _writeDictionaryBatch(Q, J, Y = !1) {
    this._dictionaryDeltaOffsets.set(J, Q.length + (this._dictionaryDeltaOffsets.get(J) || 0));
    let { byteLength: W, nodes: K, bufferRegions: z, buffers: N } = _6.assemble(new Z1([Q])), F = new $Q(Q.length, K, z), L = new KZ(F, J, Y), w = w8.from(L, W);
    return this._writeMessage(w)._writeBodyBuffers(N);
  }
  _writeBodyBuffers(Q) {
    let J, Y, W;
    for (let K = -1, z = Q.length;++K < z; )
      if ((J = Q[K]) && (Y = J.byteLength) > 0) {
        if (this._write(J), (W = (Y + 7 & -8) - Y) > 0)
          this._writePadding(W);
      }
    return this;
  }
  _writeDictionaries(Q) {
    for (let [J, Y] of Q.dictionaries) {
      let W = this._dictionaryDeltaOffsets.get(J) || 0;
      if (W === 0 || (Y = Y === null || Y === void 0 ? void 0 : Y.slice(W)).length > 0)
        for (let K of Y.data)
          this._writeDictionaryBatch(K, J, W > 0), W += K.length;
    }
    return this;
  }
}

class g$ extends Dq {
  static writeAll(Q, J) {
    let Y = new g$(J);
    if (QZ(Q))
      return Q.then((W) => Y.writeAll(W));
    else if (OZ(Q))
      return mE(Y, Q);
    return fE(Y, Q);
  }
}

class x$ extends Dq {
  static writeAll(Q) {
    let J = new x$;
    if (QZ(Q))
      return Q.then((Y) => J.writeAll(Y));
    else if (OZ(Q))
      return mE(J, Q);
    return fE(J, Q);
  }
  constructor() {
    super();
    this._autoDestroy = !0;
  }
  _writeSchema(Q) {
    return this._writeMagic()._writePadding(2);
  }
  _writeFooter(Q) {
    let J = IJ.encode(new IJ(Q, A8.V4, this._recordBatchBlocks, this._dictionaryBlocks));
    return super._writeFooter(Q)._write(J)._write(Int32Array.of(J.byteLength))._writeMagic();
  }
}
function fE(Q, J) {
  let Y = J;
  if (J instanceof J8)
    Y = J.batches, Q.reset(void 0, J.schema);
  for (let W of Y)
    Q.write(W);
  return Q.finish();
}
function mE(Q, J) {
  var Y, W, K, z;
  return U0(this, void 0, void 0, function* () {
    try {
      for (Y = ZX(J);W = yield Y.next(), !W.done; ) {
        let N = W.value;
        Q.write(N);
      }
    } catch (N) {
      K = { error: N };
    } finally {
      try {
        if (W && !W.done && (z = Y.return))
          yield z.call(Y);
      } finally {
        if (K)
          throw K.error;
      }
    }
    return Q.finish();
  });
}

// node_modules/apache-arrow/io/whatwg/iterable.mjs
function mD(Q, J) {
  if (OZ(Q))
    return Py(Q, J);
  if (XX(Q))
    return Uy(Q, J);
  throw new Error("toDOMStream() must be called with an Iterable or AsyncIterable");
}
function Uy(Q, J) {
  let Y = null, W = (J === null || J === void 0 ? void 0 : J.type) === "bytes" || !1, K = (J === null || J === void 0 ? void 0 : J.highWaterMark) || Math.pow(2, 24);
  return new ReadableStream(Object.assign(Object.assign({}, J), {
    start(N) {
      z(N, Y || (Y = Q[Symbol.iterator]()));
    },
    pull(N) {
      Y ? z(N, Y) : N.close();
    },
    cancel() {
      ((Y === null || Y === void 0 ? void 0 : Y.return) && Y.return() || !0) && (Y = null);
    }
  }), Object.assign({ highWaterMark: W ? K : void 0 }, J));
  function z(N, F) {
    let L, w = null, D = N.desiredSize || null;
    while (!(w = F.next(W ? D : null)).done) {
      if (ArrayBuffer.isView(w.value) && (L = n0(w.value)))
        D != null && W && (D = D - L.byteLength + 1), w.value = L;
      if (N.enqueue(w.value), D != null && --D <= 0)
        return;
    }
    N.close();
  }
}
function Py(Q, J) {
  let Y = null, W = (J === null || J === void 0 ? void 0 : J.type) === "bytes" || !1, K = (J === null || J === void 0 ? void 0 : J.highWaterMark) || Math.pow(2, 24);
  return new ReadableStream(Object.assign(Object.assign({}, J), {
    start(N) {
      return U0(this, void 0, void 0, function* () {
        yield z(N, Y || (Y = Q[Symbol.asyncIterator]()));
      });
    },
    pull(N) {
      return U0(this, void 0, void 0, function* () {
        Y ? yield z(N, Y) : N.close();
      });
    },
    cancel() {
      return U0(this, void 0, void 0, function* () {
        ((Y === null || Y === void 0 ? void 0 : Y.return) && (yield Y.return()) || !0) && (Y = null);
      });
    }
  }), Object.assign({ highWaterMark: W ? K : void 0 }, J));
  function z(N, F) {
    return U0(this, void 0, void 0, function* () {
      let L, w = null, D = N.desiredSize || null;
      while (!(w = yield F.next(W ? D : null)).done) {
        if (ArrayBuffer.isView(w.value) && (L = n0(w.value)))
          D != null && W && (D = D - L.byteLength + 1), w.value = L;
        if (N.enqueue(w.value), D != null && --D <= 0)
          return;
      }
      N.close();
    });
  }
}

// node_modules/apache-arrow/io/whatwg/builder.mjs
function cD(Q) {
  return new pD(Q);
}

class pD {
  constructor(Q) {
    this._numChunks = 0, this._finished = !1, this._bufferedSize = 0;
    let { ["readableStrategy"]: J, ["writableStrategy"]: Y, ["queueingStrategy"]: W = "count" } = Q, K = ow(Q, ["readableStrategy", "writableStrategy", "queueingStrategy"]);
    this._controller = null, this._builder = I$(K), this._getSize = W !== "bytes" ? bD : uD;
    let { ["highWaterMark"]: z = W === "bytes" ? Math.pow(2, 14) : 1000 } = Object.assign({}, J), { ["highWaterMark"]: N = W === "bytes" ? Math.pow(2, 14) : 1000 } = Object.assign({}, Y);
    this.readable = new ReadableStream({
      ["cancel"]: () => {
        this._builder.clear();
      },
      ["pull"]: (F) => {
        this._maybeFlush(this._builder, this._controller = F);
      },
      ["start"]: (F) => {
        this._maybeFlush(this._builder, this._controller = F);
      }
    }, {
      highWaterMark: z,
      size: W !== "bytes" ? bD : uD
    }), this.writable = new WritableStream({
      ["abort"]: () => {
        this._builder.clear();
      },
      ["write"]: () => {
        this._maybeFlush(this._builder, this._controller);
      },
      ["close"]: () => {
        this._maybeFlush(this._builder.finish(), this._controller);
      }
    }, {
      highWaterMark: N,
      size: (F) => this._writeValueAndReturnChunkSize(F)
    });
  }
  _writeValueAndReturnChunkSize(Q) {
    let J = this._bufferedSize;
    return this._bufferedSize = this._getSize(this._builder.append(Q)), this._bufferedSize - J;
  }
  _maybeFlush(Q, J) {
    if (J == null)
      return;
    if (this._bufferedSize >= J.desiredSize)
      ++this._numChunks && this._enqueue(J, Q.toVector());
    if (Q.finished) {
      if (Q.length > 0 || this._numChunks === 0)
        ++this._numChunks && this._enqueue(J, Q.toVector());
      if (!this._finished && (this._finished = !0))
        this._enqueue(J, null);
    }
  }
  _enqueue(Q, J) {
    this._bufferedSize = 0, this._controller = null, J == null ? Q.close() : Q.enqueue(J);
  }
}
var bD = (Q) => {
  var J;
  return (J = Q === null || Q === void 0 ? void 0 : Q.length) !== null && J !== void 0 ? J : 0;
}, uD = (Q) => {
  var J;
  return (J = Q === null || Q === void 0 ? void 0 : Q.byteLength) !== null && J !== void 0 ? J : 0;
};

// node_modules/apache-arrow/io/whatwg/reader.mjs
function fH(Q, J) {
  let Y = new R4, W = null, K = new ReadableStream({
    cancel() {
      return U0(this, void 0, void 0, function* () {
        yield Y.close();
      });
    },
    start(F) {
      return U0(this, void 0, void 0, function* () {
        yield N(F, W || (W = yield z()));
      });
    },
    pull(F) {
      return U0(this, void 0, void 0, function* () {
        W ? yield N(F, W) : F.close();
      });
    }
  });
  return { writable: new WritableStream(Y, Object.assign({ highWaterMark: Math.pow(2, 14) }, Q)), readable: K };
  function z() {
    return U0(this, void 0, void 0, function* () {
      return yield (yield MQ.from(Y)).open(J);
    });
  }
  function N(F, L) {
    return U0(this, void 0, void 0, function* () {
      let w = F.desiredSize, D = null;
      while (!(D = yield L.next()).done)
        if (F.enqueue(D.value), w != null && --w <= 0)
          return;
      F.close();
    });
  }
}

// node_modules/apache-arrow/io/whatwg/writer.mjs
function mH(Q, J) {
  let Y = new this(Q), W = new IZ(Y), K = new ReadableStream({
    cancel() {
      return U0(this, void 0, void 0, function* () {
        yield W.cancel();
      });
    },
    pull(N) {
      return U0(this, void 0, void 0, function* () {
        yield z(N);
      });
    },
    start(N) {
      return U0(this, void 0, void 0, function* () {
        yield z(N);
      });
    }
  }, Object.assign({ highWaterMark: Math.pow(2, 14) }, J));
  return { writable: new WritableStream(Y, Q), readable: K };
  function z(N) {
    return U0(this, void 0, void 0, function* () {
      let F = null, L = N.desiredSize;
      while (F = yield W.read(L || null))
        if (N.enqueue(F), L != null && (L -= F.byteLength) <= 0)
          return;
      N.close();
    });
  }
}
// node_modules/apache-arrow/ipc/serialization.mjs
function hJ(Q) {
  let J = MQ.from(Q);
  if (QZ(J))
    return J.then((Y) => hJ(Y));
  if (J.isAsync())
    return J.readAll().then((Y) => new J8(Y));
  return new J8(J.readAll());
}
function kq(Q, J = "stream") {
  return (J === "stream" ? g$ : x$).writeAll(Q).toUint8Array(!0);
}
// node_modules/apache-arrow/Arrow.mjs
var Ay = Object.assign(Object.assign(Object.assign(Object.assign(Object.assign(Object.assign(Object.assign({}, SN), JE), iN), bN), BN), rN), {
  compareSchemas: _$,
  compareFields: ND,
  compareTypes: ED
});
// node_modules/apache-arrow/Arrow.dom.mjs
y8.toDOMStream = mD;
U6.throughDOM = cD;
MQ.throughDOM = fH;
Mq.throughDOM = fH;
xJ.throughDOM = fH;
Dq.throughDOM = mH;
x$.throughDOM = mH;
g$.throughDOM = mH;

// node_modules/streamlit-component-lib/dist/ArrowTable.js
var bH = function() {
  function Q(J, Y, W, K) {
    var z = this;
    this.getCell = function(N, F) {
      var L = N < z.headerRows && F < z.headerColumns, w = N >= z.headerRows && F < z.headerColumns, D = N < z.headerRows && F >= z.headerColumns;
      if (L) {
        var R = ["blank"];
        if (F > 0)
          R.push("level" + N);
        return {
          type: "blank",
          classNames: R.join(" "),
          content: ""
        };
      } else if (D) {
        var V = F - z.headerColumns, R = [
          "col_heading",
          "level" + N,
          "col" + V
        ];
        return {
          type: "columns",
          classNames: R.join(" "),
          content: z.getContent(z.columnsTable, V, N)
        };
      } else if (w) {
        var g = N - z.headerRows, R = [
          "row_heading",
          "level" + F,
          "row" + g
        ];
        return {
          type: "index",
          id: "T_".concat(z.uuid, "level").concat(F, "_row").concat(g),
          classNames: R.join(" "),
          content: z.getContent(z.indexTable, g, F)
        };
      } else {
        var g = N - z.headerRows, V = F - z.headerColumns, R = [
          "data",
          "row" + g,
          "col" + V
        ], s = z.styler ? z.getContent(z.styler.displayValuesTable, g, V) : z.getContent(z.dataTable, g, V);
        return {
          type: "data",
          id: "T_".concat(z.uuid, "row").concat(g, "_col").concat(V),
          classNames: R.join(" "),
          content: s
        };
      }
    }, this.getContent = function(N, F, L) {
      var w = N.getChildAt(L);
      if (w === null)
        return "";
      var D = z.getColumnTypeId(N, L);
      switch (D) {
        case I.Timestamp:
          return z.nanosToDate(w.get(F));
        default:
          return w.get(F);
      }
    }, this.dataTable = hJ(J), this.indexTable = hJ(Y), this.columnsTable = hJ(W), this.styler = K ? {
      caption: K.caption,
      displayValuesTable: hJ(K.displayValues),
      styles: K.styles,
      uuid: K.uuid
    } : void 0;
  }
  return Object.defineProperty(Q.prototype, "rows", {
    get: function() {
      return this.indexTable.numRows + this.columnsTable.numCols;
    },
    enumerable: !1,
    configurable: !0
  }), Object.defineProperty(Q.prototype, "columns", {
    get: function() {
      return this.indexTable.numCols + this.columnsTable.numRows;
    },
    enumerable: !1,
    configurable: !0
  }), Object.defineProperty(Q.prototype, "headerRows", {
    get: function() {
      return this.rows - this.dataRows;
    },
    enumerable: !1,
    configurable: !0
  }), Object.defineProperty(Q.prototype, "headerColumns", {
    get: function() {
      return this.columns - this.dataColumns;
    },
    enumerable: !1,
    configurable: !0
  }), Object.defineProperty(Q.prototype, "dataRows", {
    get: function() {
      return this.dataTable.numRows;
    },
    enumerable: !1,
    configurable: !0
  }), Object.defineProperty(Q.prototype, "dataColumns", {
    get: function() {
      return this.dataTable.numCols;
    },
    enumerable: !1,
    configurable: !0
  }), Object.defineProperty(Q.prototype, "uuid", {
    get: function() {
      return this.styler && this.styler.uuid;
    },
    enumerable: !1,
    configurable: !0
  }), Object.defineProperty(Q.prototype, "caption", {
    get: function() {
      return this.styler && this.styler.caption;
    },
    enumerable: !1,
    configurable: !0
  }), Object.defineProperty(Q.prototype, "styles", {
    get: function() {
      return this.styler && this.styler.styles;
    },
    enumerable: !1,
    configurable: !0
  }), Object.defineProperty(Q.prototype, "table", {
    get: function() {
      return this.dataTable;
    },
    enumerable: !1,
    configurable: !0
  }), Object.defineProperty(Q.prototype, "index", {
    get: function() {
      return this.indexTable;
    },
    enumerable: !1,
    configurable: !0
  }), Object.defineProperty(Q.prototype, "columnTable", {
    get: function() {
      return this.columnsTable;
    },
    enumerable: !1,
    configurable: !0
  }), Q.prototype.serialize = function() {
    return {
      data: kq(this.dataTable),
      index: kq(this.indexTable),
      columns: kq(this.columnsTable)
    };
  }, Q.prototype.getColumnTypeId = function(J, Y) {
    return J.schema.fields[Y].type.typeId;
  }, Q.prototype.nanosToDate = function(J) {
    return new Date(J / 1e6);
  }, Q;
}();

// node_modules/streamlit-component-lib/dist/streamlit.js
var r3 = function() {
  return r3 = Object.assign || function(Q) {
    for (var J, Y = 1, W = arguments.length;Y < W; Y++) {
      J = arguments[Y];
      for (var K in J)
        if (Object.prototype.hasOwnProperty.call(J, K))
          Q[K] = J[K];
    }
    return Q;
  }, r3.apply(this, arguments);
}, i3;
(function(Q) {
  Q.COMPONENT_READY = "streamlit:componentReady", Q.SET_COMPONENT_VALUE = "streamlit:setComponentValue", Q.SET_FRAME_HEIGHT = "streamlit:setFrameHeight";
})(i3 || (i3 = {}));
var uQ = function() {
  function Q() {}
  return Q.API_VERSION = 1, Q.RENDER_EVENT = "streamlit:render", Q.events = new EventTarget, Q.registeredMessageListener = !1, Q.setComponentReady = function() {
    if (!Q.registeredMessageListener)
      window.addEventListener("message", Q.onMessageEvent), Q.registeredMessageListener = !0;
    Q.sendBackMsg(i3.COMPONENT_READY, {
      apiVersion: Q.API_VERSION
    });
  }, Q.setFrameHeight = function(J) {
    if (J === void 0)
      J = document.body.scrollHeight;
    if (J === Q.lastFrameHeight)
      return;
    Q.lastFrameHeight = J, Q.sendBackMsg(i3.SET_FRAME_HEIGHT, { height: J });
  }, Q.setComponentValue = function(J) {
    var Y;
    if (J instanceof bH)
      Y = "dataframe", J = J.serialize();
    else if (Oy(J))
      Y = "bytes", J = new Uint8Array(J.buffer);
    else if (J instanceof ArrayBuffer)
      Y = "bytes", J = new Uint8Array(J);
    else
      Y = "json";
    Q.sendBackMsg(i3.SET_COMPONENT_VALUE, {
      value: J,
      dataType: Y
    });
  }, Q.onMessageEvent = function(J) {
    var Y = J.data.type;
    switch (Y) {
      case Q.RENDER_EVENT:
        Q.onRenderMessage(J.data);
        break;
    }
  }, Q.onRenderMessage = function(J) {
    var Y = J.args;
    if (Y == null)
      console.error("Got null args in onRenderMessage. This should never happen"), Y = {};
    var W = J.dfs && J.dfs.length > 0 ? Q.argsDataframeToObject(J.dfs) : {};
    Y = r3(r3({}, Y), W);
    var K = Boolean(J.disabled), z = J.theme;
    if (z)
      Ly(z);
    var N = { disabled: K, args: Y, theme: z }, F = new CustomEvent(Q.RENDER_EVENT, {
      detail: N
    });
    Q.events.dispatchEvent(F);
  }, Q.argsDataframeToObject = function(J) {
    var Y = J.map(function(W) {
      var { key: K, value: z } = W;
      return [K, Q.toArrowTable(z)];
    });
    return Object.fromEntries(Y);
  }, Q.toArrowTable = function(J) {
    var Y, W = (Y = J.data, Y.data), K = Y.index, z = Y.columns, N = Y.styler;
    return new bH(W, K, z, N);
  }, Q.sendBackMsg = function(J, Y) {
    window.parent.postMessage(r3({ isStreamlitMessage: !0, type: J }, Y), "*");
  }, Q;
}(), Ly = function(Q) {
  var J = document.createElement("style");
  document.head.appendChild(J), J.innerHTML = `
    :root {
      --primary-color: `.concat(Q.primaryColor, `;
      --background-color: `).concat(Q.backgroundColor, `;
      --secondary-background-color: `).concat(Q.secondaryBackgroundColor, `;
      --text-color: `).concat(Q.textColor, `;
      --font: `).concat(Q.font, `;
    }

    body {
      background-color: var(--background-color);
      color: var(--text-color);
    }
  `);
};
function Oy(Q) {
  var J = !1;
  try {
    J = Q instanceof BigInt64Array || Q instanceof BigUint64Array;
  } catch (Y) {}
  return Q instanceof Int8Array || Q instanceof Uint8Array || Q instanceof Uint8ClampedArray || Q instanceof Int16Array || Q instanceof Uint16Array || Q instanceof Int32Array || Q instanceof Uint32Array || Q instanceof Float32Array || Q instanceof Float64Array || J;
}

// node_modules/streamlit-component-lib/dist/StreamlitReact.js
var dD = function() {
  var Q = function(J, Y) {
    return Q = Object.setPrototypeOf || { __proto__: [] } instanceof Array && function(W, K) {
      W.__proto__ = K;
    } || function(W, K) {
      for (var z in K)
        if (Object.prototype.hasOwnProperty.call(K, z))
          W[z] = K[z];
    }, Q(J, Y);
  };
  return function(J, Y) {
    if (typeof Y !== "function" && Y !== null)
      throw new TypeError("Class extends value " + String(Y) + " is not a constructor or null");
    Q(J, Y);
    function W() {
      this.constructor = J;
    }
    J.prototype = Y === null ? Object.create(Y) : (W.prototype = Y.prototype, new W);
  };
}(), bE = function(Q) {
  dD(J, Q);
  function J() {
    return Q !== null && Q.apply(this, arguments) || this;
  }
  return J.prototype.componentDidMount = function() {
    uQ.setFrameHeight();
  }, J.prototype.componentDidUpdate = function() {
    uQ.setFrameHeight();
  }, J;
}(v$.default.PureComponent);
function uE(Q) {
  var J = function(Y) {
    dD(W, Y);
    function W(K) {
      var z = Y.call(this, K) || this;
      return z.componentDidMount = function() {
        uQ.events.addEventListener(uQ.RENDER_EVENT, z.onRenderEvent), uQ.setComponentReady();
      }, z.componentDidUpdate = function() {
        if (z.state.componentError != null)
          uQ.setFrameHeight();
      }, z.componentWillUnmount = function() {
        uQ.events.removeEventListener(uQ.RENDER_EVENT, z.onRenderEvent);
      }, z.onRenderEvent = function(N) {
        z.setState({ renderData: N.detail });
      }, z.state = {
        renderData: void 0,
        componentError: void 0
      }, z;
    }
    return W.prototype.render = function() {
      if (this.state.componentError != null)
        return v$.default.createElement("div", null, v$.default.createElement("h1", null, "Component Error"), v$.default.createElement("span", null, this.state.componentError.message));
      if (this.state.renderData == null)
        return null;
      return v$.default.createElement(Q, { width: window.innerWidth, disabled: this.state.renderData.disabled, args: this.state.renderData.args, theme: this.state.renderData.theme });
    }, W.getDerivedStateFromError = function(K) {
      return { componentError: K };
    }, W;
  }(v$.default.PureComponent);
  return lD.default(J, Q);
}
// src/StreamlitWrapper.tsx
var nR = D6(LQ(), 1);

// src/ContigsOrganizer.tsx
var D1 = D6(LQ(), 1);

// node_modules/@dnd-kit/core/dist/core.esm.js
var u = D6(LQ(), 1), fJ = D6(PN(), 1);

// node_modules/@dnd-kit/utilities/dist/utilities.esm.js
var T6 = D6(LQ(), 1);
function sD() {
  for (var Q = arguments.length, J = new Array(Q), Y = 0;Y < Q; Y++)
    J[Y] = arguments[Y];
  return T6.useMemo(() => (W) => {
    J.forEach((K) => K(W));
  }, J);
}
var t3 = typeof window !== "undefined" && typeof window.document !== "undefined" && typeof window.document.createElement !== "undefined";
function h$(Q) {
  let J = Object.prototype.toString.call(Q);
  return J === "[object Window]" || J === "[object global]";
}
function uH(Q) {
  return "nodeType" in Q;
}
function YQ(Q) {
  var J, Y;
  if (!Q)
    return window;
  if (h$(Q))
    return Q;
  if (!uH(Q))
    return window;
  return (J = (Y = Q.ownerDocument) == null ? void 0 : Y.defaultView) != null ? J : window;
}
function cH(Q) {
  let {
    Document: J
  } = YQ(Q);
  return Q instanceof J;
}
function Rq(Q) {
  if (h$(Q))
    return !1;
  return Q instanceof YQ(Q).HTMLElement;
}
function pE(Q) {
  return Q instanceof YQ(Q).SVGElement;
}
function y$(Q) {
  if (!Q)
    return document;
  if (h$(Q))
    return Q.document;
  if (!uH(Q))
    return document;
  if (cH(Q))
    return Q;
  if (Rq(Q) || pE(Q))
    return Q.ownerDocument;
  return document;
}
var cQ = t3 ? T6.useLayoutEffect : T6.useEffect;
function e3(Q) {
  let J = T6.useRef(Q);
  return cQ(() => {
    J.current = Q;
  }), T6.useCallback(function() {
    for (var Y = arguments.length, W = new Array(Y), K = 0;K < Y; K++)
      W[K] = arguments[K];
    return J.current == null ? void 0 : J.current(...W);
  }, []);
}
function oD() {
  let Q = T6.useRef(null), J = T6.useCallback((W, K) => {
    Q.current = setInterval(W, K);
  }, []), Y = T6.useCallback(() => {
    if (Q.current !== null)
      clearInterval(Q.current), Q.current = null;
  }, []);
  return [J, Y];
}
function jq(Q, J) {
  if (J === void 0)
    J = [Q];
  let Y = T6.useRef(Q);
  return cQ(() => {
    if (Y.current !== Q)
      Y.current = Q;
  }, J), Y;
}
function Bq(Q, J) {
  let Y = T6.useRef();
  return T6.useMemo(() => {
    let W = Q(Y.current);
    return Y.current = W, W;
  }, [...J]);
}
function QK(Q) {
  let J = e3(Q), Y = T6.useRef(null), W = T6.useCallback((K) => {
    if (K !== Y.current)
      J == null || J(K, Y.current);
    Y.current = K;
  }, []);
  return [Y, W];
}
function ZK(Q) {
  let J = T6.useRef();
  return T6.useEffect(() => {
    J.current = Q;
  }, [Q]), J.current;
}
var cE = {};
function f$(Q, J) {
  return T6.useMemo(() => {
    if (J)
      return J;
    let Y = cE[Q] == null ? 0 : cE[Q] + 1;
    return cE[Q] = Y, Q + "-" + Y;
  }, [Q, J]);
}
function aD(Q) {
  return function(J) {
    for (var Y = arguments.length, W = new Array(Y > 1 ? Y - 1 : 0), K = 1;K < Y; K++)
      W[K - 1] = arguments[K];
    return W.reduce((z, N) => {
      let F = Object.entries(N);
      for (let [L, w] of F) {
        let D = z[L];
        if (D != null)
          z[L] = D + Q * w;
      }
      return z;
    }, {
      ...J
    });
  };
}
var m$ = /* @__PURE__ */ aD(1), b$ = /* @__PURE__ */ aD(-1);
function wy(Q) {
  return "clientX" in Q && "clientY" in Q;
}
function Cq(Q) {
  if (!Q)
    return !1;
  let {
    KeyboardEvent: J
  } = YQ(Q.target);
  return J && Q instanceof J;
}
function My(Q) {
  if (!Q)
    return !1;
  let {
    TouchEvent: J
  } = YQ(Q.target);
  return J && Q instanceof J;
}
function XK(Q) {
  if (My(Q)) {
    if (Q.touches && Q.touches.length) {
      let {
        clientX: J,
        clientY: Y
      } = Q.touches[0];
      return {
        x: J,
        y: Y
      };
    } else if (Q.changedTouches && Q.changedTouches.length) {
      let {
        clientX: J,
        clientY: Y
      } = Q.changedTouches[0];
      return {
        x: J,
        y: Y
      };
    }
  }
  if (wy(Q))
    return {
      x: Q.clientX,
      y: Q.clientY
    };
  return null;
}
var GX = /* @__PURE__ */ Object.freeze({
  Translate: {
    toString(Q) {
      if (!Q)
        return;
      let {
        x: J,
        y: Y
      } = Q;
      return "translate3d(" + (J ? Math.round(J) : 0) + "px, " + (Y ? Math.round(Y) : 0) + "px, 0)";
    }
  },
  Scale: {
    toString(Q) {
      if (!Q)
        return;
      let {
        scaleX: J,
        scaleY: Y
      } = Q;
      return "scaleX(" + J + ") scaleY(" + Y + ")";
    }
  },
  Transform: {
    toString(Q) {
      if (!Q)
        return;
      return [GX.Translate.toString(Q), GX.Scale.toString(Q)].join(" ");
    }
  },
  Transition: {
    toString(Q) {
      let {
        property: J,
        duration: Y,
        easing: W
      } = Q;
      return J + " " + Y + "ms " + W;
    }
  }
}), nD = "a,frame,iframe,input:not([type=hidden]):not(:disabled),select:not(:disabled),textarea:not(:disabled),button:not(:disabled),*[tabindex]";
function rD(Q) {
  if (Q.matches(nD))
    return Q;
  return Q.querySelector(nD);
}

// node_modules/@dnd-kit/accessibility/dist/accessibility.esm.js
var u$ = D6(LQ(), 1), Dy = {
  display: "none"
};
function iD(Q) {
  let {
    id: J,
    value: Y
  } = Q;
  return u$.default.createElement("div", {
    id: J,
    style: Dy
  }, Y);
}
function tD(Q) {
  let {
    id: J,
    announcement: Y,
    ariaLiveType: W = "assertive"
  } = Q, K = {
    position: "fixed",
    width: 1,
    height: 1,
    margin: -1,
    border: 0,
    padding: 0,
    overflow: "hidden",
    clip: "rect(0 0 0 0)",
    clipPath: "inset(100%)",
    whiteSpace: "nowrap"
  };
  return u$.default.createElement("div", {
    id: J,
    style: K,
    role: "status",
    "aria-live": W,
    "aria-atomic": !0
  }, Y);
}
function eD() {
  let [Q, J] = u$.useState("");
  return {
    announce: u$.useCallback((W) => {
      if (W != null)
        J(W);
    }, []),
    announcement: Q
  };
}

// node_modules/@dnd-kit/core/dist/core.esm.js
var zk = /* @__PURE__ */ u.createContext(null);
function ky(Q) {
  let J = u.useContext(zk);
  u.useEffect(() => {
    if (!J)
      throw new Error("useDndMonitor must be used within a children of <DndContext>");
    return J(Q);
  }, [Q, J]);
}
function Ry() {
  let [Q] = u.useState(() => /* @__PURE__ */ new Set), J = u.useCallback((W) => {
    return Q.add(W), () => Q.delete(W);
  }, [Q]);
  return [u.useCallback((W) => {
    let {
      type: K,
      event: z
    } = W;
    Q.forEach((N) => {
      var F;
      return (F = N[K]) == null ? void 0 : F.call(N, z);
    });
  }, [Q]), J];
}
var jy = {
  draggable: `
    To pick up a draggable item, press the space bar.
    While dragging, use the arrow keys to move the item.
    Press space again to drop the item in its new position, or press escape to cancel.
  `
}, By = {
  onDragStart(Q) {
    let {
      active: J
    } = Q;
    return "Picked up draggable item " + J.id + ".";
  },
  onDragOver(Q) {
    let {
      active: J,
      over: Y
    } = Q;
    if (Y)
      return "Draggable item " + J.id + " was moved over droppable area " + Y.id + ".";
    return "Draggable item " + J.id + " is no longer over a droppable area.";
  },
  onDragEnd(Q) {
    let {
      active: J,
      over: Y
    } = Q;
    if (Y)
      return "Draggable item " + J.id + " was dropped over droppable area " + Y.id;
    return "Draggable item " + J.id + " was dropped.";
  },
  onDragCancel(Q) {
    let {
      active: J
    } = Q;
    return "Dragging was cancelled. Draggable item " + J.id + " was dropped.";
  }
};
function Cy(Q) {
  let {
    announcements: J = By,
    container: Y,
    hiddenTextDescribedById: W,
    screenReaderInstructions: K = jy
  } = Q, {
    announce: z,
    announcement: N
  } = eD(), F = f$("DndLiveRegion"), [L, w] = u.useState(!1);
  if (u.useEffect(() => {
    w(!0);
  }, []), ky(u.useMemo(() => ({
    onDragStart(R) {
      let {
        active: V
      } = R;
      z(J.onDragStart({
        active: V
      }));
    },
    onDragMove(R) {
      let {
        active: V,
        over: g
      } = R;
      if (J.onDragMove)
        z(J.onDragMove({
          active: V,
          over: g
        }));
    },
    onDragOver(R) {
      let {
        active: V,
        over: g
      } = R;
      z(J.onDragOver({
        active: V,
        over: g
      }));
    },
    onDragEnd(R) {
      let {
        active: V,
        over: g
      } = R;
      z(J.onDragEnd({
        active: V,
        over: g
      }));
    },
    onDragCancel(R) {
      let {
        active: V,
        over: g
      } = R;
      z(J.onDragCancel({
        active: V,
        over: g
      }));
    }
  }), [z, J])), !L)
    return null;
  let D = u.default.createElement(u.default.Fragment, null, u.default.createElement(iD, {
    id: W,
    value: K.draggable
  }), u.default.createElement(tD, {
    id: F,
    announcement: N
  }));
  return Y ? fJ.createPortal(D, Y) : D;
}
var Y8;
(function(Q) {
  Q.DragStart = "dragStart", Q.DragMove = "dragMove", Q.DragEnd = "dragEnd", Q.DragCancel = "dragCancel", Q.DragOver = "dragOver", Q.RegisterDroppable = "registerDroppable", Q.SetDroppableDisabled = "setDroppableDisabled", Q.UnregisterDroppable = "unregisterDroppable";
})(Y8 || (Y8 = {}));
function dH() {}
function Iq(Q, J) {
  return u.useMemo(() => ({
    sensor: Q,
    options: J != null ? J : {}
  }), [Q, J]);
}
function nH() {
  for (var Q = arguments.length, J = new Array(Q), Y = 0;Y < Q; Y++)
    J[Y] = arguments[Y];
  return u.useMemo(() => [...J].filter((W) => W != null), [...J]);
}
var zX = /* @__PURE__ */ Object.freeze({
  x: 0,
  y: 0
});
function Vy(Q, J) {
  return Math.sqrt(Math.pow(Q.x - J.x, 2) + Math.pow(Q.y - J.y, 2));
}
function Sy(Q, J) {
  let Y = XK(Q);
  if (!Y)
    return "0 0";
  let W = {
    x: (Y.x - J.left) / J.width * 100,
    y: (Y.y - J.top) / J.height * 100
  };
  return W.x + "% " + W.y + "%";
}
function Iy(Q, J) {
  let {
    data: {
      value: Y
    }
  } = Q, {
    data: {
      value: W
    }
  } = J;
  return Y - W;
}
function _y(Q, J) {
  let {
    data: {
      value: Y
    }
  } = Q, {
    data: {
      value: W
    }
  } = J;
  return W - Y;
}
function Qk(Q) {
  let {
    left: J,
    top: Y,
    height: W,
    width: K
  } = Q;
  return [{
    x: J,
    y: Y
  }, {
    x: J + K,
    y: Y
  }, {
    x: J,
    y: Y + W
  }, {
    x: J + K,
    y: Y + W
  }];
}
function iE(Q, J) {
  if (!Q || Q.length === 0)
    return null;
  let [Y] = Q;
  return J ? Y[J] : Y;
}
var Nk = (Q) => {
  let {
    collisionRect: J,
    droppableRects: Y,
    droppableContainers: W
  } = Q, K = Qk(J), z = [];
  for (let N of W) {
    let {
      id: F
    } = N, L = Y.get(F);
    if (L) {
      let w = Qk(L), D = K.reduce((V, g, s) => {
        return V + Vy(w[s], g);
      }, 0), R = Number((D / 4).toFixed(4));
      z.push({
        id: F,
        data: {
          droppableContainer: N,
          value: R
        }
      });
    }
  }
  return z.sort(Iy);
};
function Ty(Q, J) {
  let Y = Math.max(J.top, Q.top), W = Math.max(J.left, Q.left), K = Math.min(J.left + J.width, Q.left + Q.width), z = Math.min(J.top + J.height, Q.top + Q.height), N = K - W, F = z - Y;
  if (W < K && Y < z) {
    let L = J.width * J.height, w = Q.width * Q.height, D = N * F, R = D / (L + w - D);
    return Number(R.toFixed(4));
  }
  return 0;
}
var gy = (Q) => {
  let {
    collisionRect: J,
    droppableRects: Y,
    droppableContainers: W
  } = Q, K = [];
  for (let z of W) {
    let {
      id: N
    } = z, F = Y.get(N);
    if (F) {
      let L = Ty(F, J);
      if (L > 0)
        K.push({
          id: N,
          data: {
            droppableContainer: z,
            value: L
          }
        });
    }
  }
  return K.sort(_y);
};
function xy(Q, J, Y) {
  return {
    ...Q,
    scaleX: J && Y ? J.width / Y.width : 1,
    scaleY: J && Y ? J.height / Y.height : 1
  };
}
function Ek(Q, J) {
  return Q && J ? {
    x: Q.left - J.left,
    y: Q.top - J.top
  } : zX;
}
function vy(Q) {
  return function J(Y) {
    for (var W = arguments.length, K = new Array(W > 1 ? W - 1 : 0), z = 1;z < W; z++)
      K[z - 1] = arguments[z];
    return K.reduce((N, F) => ({
      ...N,
      top: N.top + Q * F.y,
      bottom: N.bottom + Q * F.y,
      left: N.left + Q * F.x,
      right: N.right + Q * F.x
    }), {
      ...Y
    });
  };
}
var hy = /* @__PURE__ */ vy(1);
function Fk(Q) {
  if (Q.startsWith("matrix3d(")) {
    let J = Q.slice(9, -1).split(/, /);
    return {
      x: +J[12],
      y: +J[13],
      scaleX: +J[0],
      scaleY: +J[5]
    };
  } else if (Q.startsWith("matrix(")) {
    let J = Q.slice(7, -1).split(/, /);
    return {
      x: +J[4],
      y: +J[5],
      scaleX: +J[0],
      scaleY: +J[3]
    };
  }
  return null;
}
function yy(Q, J, Y) {
  let W = Fk(J);
  if (!W)
    return Q;
  let {
    scaleX: K,
    scaleY: z,
    x: N,
    y: F
  } = W, L = Q.left - N - (1 - K) * parseFloat(Y), w = Q.top - F - (1 - z) * parseFloat(Y.slice(Y.indexOf(" ") + 1)), D = K ? Q.width / K : Q.width, R = z ? Q.height / z : Q.height;
  return {
    width: D,
    height: R,
    top: w,
    right: L + D,
    bottom: w + R,
    left: L
  };
}
var fy = {
  ignoreTransform: !1
};
function c$(Q, J) {
  if (J === void 0)
    J = fy;
  let Y = Q.getBoundingClientRect();
  if (J.ignoreTransform) {
    let {
      transform: w,
      transformOrigin: D
    } = YQ(Q).getComputedStyle(Q);
    if (w)
      Y = yy(Y, w, D);
  }
  let {
    top: W,
    left: K,
    width: z,
    height: N,
    bottom: F,
    right: L
  } = Y;
  return {
    top: W,
    left: K,
    width: z,
    height: N,
    bottom: F,
    right: L
  };
}
function Zk(Q) {
  return c$(Q, {
    ignoreTransform: !0
  });
}
function my(Q) {
  let { innerWidth: J, innerHeight: Y } = Q;
  return {
    top: 0,
    left: 0,
    right: J,
    bottom: Y,
    width: J,
    height: Y
  };
}
function by(Q, J) {
  if (J === void 0)
    J = YQ(Q).getComputedStyle(Q);
  return J.position === "fixed";
}
function uy(Q, J) {
  if (J === void 0)
    J = YQ(Q).getComputedStyle(Q);
  let Y = /(auto|scroll|overlay)/;
  return ["overflow", "overflowX", "overflowY"].some((K) => {
    let z = J[K];
    return typeof z === "string" ? Y.test(z) : !1;
  });
}
function YK(Q, J) {
  let Y = [];
  function W(K) {
    if (J != null && Y.length >= J)
      return Y;
    if (!K)
      return Y;
    if (cH(K) && K.scrollingElement != null && !Y.includes(K.scrollingElement))
      return Y.push(K.scrollingElement), Y;
    if (!Rq(K) || pE(K))
      return Y;
    if (Y.includes(K))
      return Y;
    let z = YQ(Q).getComputedStyle(K);
    if (K !== Q) {
      if (uy(K, z))
        Y.push(K);
    }
    if (by(K, z))
      return Y;
    return W(K.parentNode);
  }
  if (!Q)
    return Y;
  return W(Q);
}
function Uk(Q) {
  let [J] = YK(Q, 1);
  return J != null ? J : null;
}
function dE(Q) {
  if (!t3 || !Q)
    return null;
  if (h$(Q))
    return Q;
  if (!uH(Q))
    return null;
  if (cH(Q) || Q === y$(Q).scrollingElement)
    return window;
  if (Rq(Q))
    return Q;
  return null;
}
function Pk(Q) {
  if (h$(Q))
    return Q.scrollX;
  return Q.scrollLeft;
}
function Ak(Q) {
  if (h$(Q))
    return Q.scrollY;
  return Q.scrollTop;
}
function oE(Q) {
  return {
    x: Pk(Q),
    y: Ak(Q)
  };
}
var M8;
(function(Q) {
  Q[Q.Forward = 1] = "Forward", Q[Q.Backward = -1] = "Backward";
})(M8 || (M8 = {}));
function Lk(Q) {
  if (!t3 || !Q)
    return !1;
  return Q === document.scrollingElement;
}
function Ok(Q) {
  let J = {
    x: 0,
    y: 0
  }, Y = Lk(Q) ? {
    height: window.innerHeight,
    width: window.innerWidth
  } : {
    height: Q.clientHeight,
    width: Q.clientWidth
  }, W = {
    x: Q.scrollWidth - Y.width,
    y: Q.scrollHeight - Y.height
  }, K = Q.scrollTop <= J.y, z = Q.scrollLeft <= J.x, N = Q.scrollTop >= W.y, F = Q.scrollLeft >= W.x;
  return {
    isTop: K,
    isLeft: z,
    isBottom: N,
    isRight: F,
    maxScroll: W,
    minScroll: J
  };
}
var cy = {
  x: 0.2,
  y: 0.2
};
function py(Q, J, Y, W, K) {
  let {
    top: z,
    left: N,
    right: F,
    bottom: L
  } = Y;
  if (W === void 0)
    W = 10;
  if (K === void 0)
    K = cy;
  let {
    isTop: w,
    isBottom: D,
    isLeft: R,
    isRight: V
  } = Ok(Q), g = {
    x: 0,
    y: 0
  }, s = {
    x: 0,
    y: 0
  }, i = {
    height: J.height * K.y,
    width: J.width * K.x
  };
  if (!w && z <= J.top + i.height)
    g.y = M8.Backward, s.y = W * Math.abs((J.top + i.height - z) / i.height);
  else if (!D && L >= J.bottom - i.height)
    g.y = M8.Forward, s.y = W * Math.abs((J.bottom - i.height - L) / i.height);
  if (!V && F >= J.right - i.width)
    g.x = M8.Forward, s.x = W * Math.abs((J.right - i.width - F) / i.width);
  else if (!R && N <= J.left + i.width)
    g.x = M8.Backward, s.x = W * Math.abs((J.left + i.width - N) / i.width);
  return {
    direction: g,
    speed: s
  };
}
function dy(Q) {
  if (Q === document.scrollingElement) {
    let {
      innerWidth: z,
      innerHeight: N
    } = window;
    return {
      top: 0,
      left: 0,
      right: z,
      bottom: N,
      width: z,
      height: N
    };
  }
  let {
    top: J,
    left: Y,
    right: W,
    bottom: K
  } = Q.getBoundingClientRect();
  return {
    top: J,
    left: Y,
    right: W,
    bottom: K,
    width: Q.clientWidth,
    height: Q.clientHeight
  };
}
function wk(Q) {
  return Q.reduce((J, Y) => {
    return m$(J, oE(Y));
  }, zX);
}
function ly(Q) {
  return Q.reduce((J, Y) => {
    return J + Pk(Y);
  }, 0);
}
function ny(Q) {
  return Q.reduce((J, Y) => {
    return J + Ak(Y);
  }, 0);
}
function Mk(Q, J) {
  if (J === void 0)
    J = c$;
  if (!Q)
    return;
  let {
    top: Y,
    left: W,
    bottom: K,
    right: z
  } = J(Q);
  if (!Uk(Q))
    return;
  if (K <= 0 || z <= 0 || Y >= window.innerHeight || W >= window.innerWidth)
    Q.scrollIntoView({
      block: "center",
      inline: "center"
    });
}
var sy = [["x", ["left", "right"], ly], ["y", ["top", "bottom"], ny]];

class sH {
  constructor(Q, J) {
    this.rect = void 0, this.width = void 0, this.height = void 0, this.top = void 0, this.bottom = void 0, this.right = void 0, this.left = void 0;
    let Y = YK(J), W = wk(Y);
    this.rect = {
      ...Q
    }, this.width = Q.width, this.height = Q.height;
    for (let [K, z, N] of sy)
      for (let F of z)
        Object.defineProperty(this, F, {
          get: () => {
            let L = N(Y), w = W[K] - L;
            return this.rect[F] + w;
          },
          enumerable: !0
        });
    Object.defineProperty(this, "rect", {
      enumerable: !1
    });
  }
}

class Vq {
  constructor(Q) {
    this.target = void 0, this.listeners = [], this.removeAll = () => {
      this.listeners.forEach((J) => {
        var Y;
        return (Y = this.target) == null ? void 0 : Y.removeEventListener(...J);
      });
    }, this.target = Q;
  }
  add(Q, J, Y) {
    var W;
    (W = this.target) == null || W.addEventListener(Q, J, Y), this.listeners.push([Q, J, Y]);
  }
}
function oy(Q) {
  let {
    EventTarget: J
  } = YQ(Q);
  return Q instanceof J ? Q : y$(Q);
}
function lE(Q, J) {
  let Y = Math.abs(Q.x), W = Math.abs(Q.y);
  if (typeof J === "number")
    return Math.sqrt(Y ** 2 + W ** 2) > J;
  if ("x" in J && "y" in J)
    return Y > J.x && W > J.y;
  if ("x" in J)
    return Y > J.x;
  if ("y" in J)
    return W > J.y;
  return !1;
}
var TZ;
(function(Q) {
  Q.Click = "click", Q.DragStart = "dragstart", Q.Keydown = "keydown", Q.ContextMenu = "contextmenu", Q.Resize = "resize", Q.SelectionChange = "selectionchange", Q.VisibilityChange = "visibilitychange";
})(TZ || (TZ = {}));
function Xk(Q) {
  Q.preventDefault();
}
function ay(Q) {
  Q.stopPropagation();
}
var M1;
(function(Q) {
  Q.Space = "Space", Q.Down = "ArrowDown", Q.Right = "ArrowRight", Q.Left = "ArrowLeft", Q.Up = "ArrowUp", Q.Esc = "Escape", Q.Enter = "Enter";
})(M1 || (M1 = {}));
var Dk = {
  start: [M1.Space, M1.Enter],
  cancel: [M1.Esc],
  end: [M1.Space, M1.Enter]
}, ry = (Q, J) => {
  let {
    currentCoordinates: Y
  } = J;
  switch (Q.code) {
    case M1.Right:
      return {
        ...Y,
        x: Y.x + 25
      };
    case M1.Left:
      return {
        ...Y,
        x: Y.x - 25
      };
    case M1.Down:
      return {
        ...Y,
        y: Y.y + 25
      };
    case M1.Up:
      return {
        ...Y,
        y: Y.y - 25
      };
  }
  return;
};

class p$ {
  constructor(Q) {
    this.props = void 0, this.autoScrollEnabled = !1, this.referenceCoordinates = void 0, this.listeners = void 0, this.windowListeners = void 0, this.props = Q;
    let {
      event: {
        target: J
      }
    } = Q;
    this.props = Q, this.listeners = new Vq(y$(J)), this.windowListeners = new Vq(YQ(J)), this.handleKeyDown = this.handleKeyDown.bind(this), this.handleCancel = this.handleCancel.bind(this), this.attach();
  }
  attach() {
    this.handleStart(), this.windowListeners.add(TZ.Resize, this.handleCancel), this.windowListeners.add(TZ.VisibilityChange, this.handleCancel), setTimeout(() => this.listeners.add(TZ.Keydown, this.handleKeyDown));
  }
  handleStart() {
    let {
      activeNode: Q,
      onStart: J
    } = this.props, Y = Q.node.current;
    if (Y)
      Mk(Y);
    J(zX);
  }
  handleKeyDown(Q) {
    if (Cq(Q)) {
      let {
        active: J,
        context: Y,
        options: W
      } = this.props, {
        keyboardCodes: K = Dk,
        coordinateGetter: z = ry,
        scrollBehavior: N = "smooth"
      } = W, {
        code: F
      } = Q;
      if (K.end.includes(F)) {
        this.handleEnd(Q);
        return;
      }
      if (K.cancel.includes(F)) {
        this.handleCancel(Q);
        return;
      }
      let {
        collisionRect: L
      } = Y.current, w = L ? {
        x: L.left,
        y: L.top
      } : zX;
      if (!this.referenceCoordinates)
        this.referenceCoordinates = w;
      let D = z(Q, {
        active: J,
        context: Y.current,
        currentCoordinates: w
      });
      if (D) {
        let R = b$(D, w), V = {
          x: 0,
          y: 0
        }, {
          scrollableAncestors: g
        } = Y.current;
        for (let s of g) {
          let i = Q.code, {
            isTop: F0,
            isRight: r,
            isLeft: J0,
            isBottom: l,
            maxScroll: t,
            minScroll: $0
          } = Ok(s), M0 = dy(s), c0 = {
            x: Math.min(i === M1.Right ? M0.right - M0.width / 2 : M0.right, Math.max(i === M1.Right ? M0.left : M0.left + M0.width / 2, D.x)),
            y: Math.min(i === M1.Down ? M0.bottom - M0.height / 2 : M0.bottom, Math.max(i === M1.Down ? M0.top : M0.top + M0.height / 2, D.y))
          }, I0 = i === M1.Right && !r || i === M1.Left && !J0, p = i === M1.Down && !l || i === M1.Up && !F0;
          if (I0 && c0.x !== D.x) {
            let o = s.scrollLeft + R.x, Y0 = i === M1.Right && o <= t.x || i === M1.Left && o >= $0.x;
            if (Y0 && !R.y) {
              s.scrollTo({
                left: o,
                behavior: N
              });
              return;
            }
            if (Y0)
              V.x = s.scrollLeft - o;
            else
              V.x = i === M1.Right ? s.scrollLeft - t.x : s.scrollLeft - $0.x;
            if (V.x)
              s.scrollBy({
                left: -V.x,
                behavior: N
              });
            break;
          } else if (p && c0.y !== D.y) {
            let o = s.scrollTop + R.y, Y0 = i === M1.Down && o <= t.y || i === M1.Up && o >= $0.y;
            if (Y0 && !R.x) {
              s.scrollTo({
                top: o,
                behavior: N
              });
              return;
            }
            if (Y0)
              V.y = s.scrollTop - o;
            else
              V.y = i === M1.Down ? s.scrollTop - t.y : s.scrollTop - $0.y;
            if (V.y)
              s.scrollBy({
                top: -V.y,
                behavior: N
              });
            break;
          }
        }
        this.handleMove(Q, m$(b$(D, this.referenceCoordinates), V));
      }
    }
  }
  handleMove(Q, J) {
    let {
      onMove: Y
    } = this.props;
    Q.preventDefault(), Y(J);
  }
  handleEnd(Q) {
    let {
      onEnd: J
    } = this.props;
    Q.preventDefault(), this.detach(), J();
  }
  handleCancel(Q) {
    let {
      onCancel: J
    } = this.props;
    Q.preventDefault(), this.detach(), J();
  }
  detach() {
    this.listeners.removeAll(), this.windowListeners.removeAll();
  }
}
p$.activators = [{
  eventName: "onKeyDown",
  handler: (Q, J, Y) => {
    let {
      keyboardCodes: W = Dk,
      onActivation: K
    } = J, {
      active: z
    } = Y, {
      code: N
    } = Q.nativeEvent;
    if (W.start.includes(N)) {
      let F = z.activatorNode.current;
      if (F && Q.target !== F)
        return !1;
      return Q.preventDefault(), K == null || K({
        event: Q.nativeEvent
      }), !0;
    }
    return !1;
  }
}];
function Jk(Q) {
  return Boolean(Q && "distance" in Q);
}
function $k(Q) {
  return Boolean(Q && "delay" in Q);
}

class oH {
  constructor(Q, J, Y) {
    var W;
    if (Y === void 0)
      Y = oy(Q.event.target);
    this.props = void 0, this.events = void 0, this.autoScrollEnabled = !0, this.document = void 0, this.activated = !1, this.initialCoordinates = void 0, this.timeoutId = null, this.listeners = void 0, this.documentListeners = void 0, this.windowListeners = void 0, this.props = Q, this.events = J;
    let {
      event: K
    } = Q, {
      target: z
    } = K;
    this.props = Q, this.events = J, this.document = y$(z), this.documentListeners = new Vq(this.document), this.listeners = new Vq(Y), this.windowListeners = new Vq(YQ(z)), this.initialCoordinates = (W = XK(K)) != null ? W : zX, this.handleStart = this.handleStart.bind(this), this.handleMove = this.handleMove.bind(this), this.handleEnd = this.handleEnd.bind(this), this.handleCancel = this.handleCancel.bind(this), this.handleKeydown = this.handleKeydown.bind(this), this.removeTextSelection = this.removeTextSelection.bind(this), this.attach();
  }
  attach() {
    let {
      events: Q,
      props: {
        options: {
          activationConstraint: J,
          bypassActivationConstraint: Y
        }
      }
    } = this;
    if (this.listeners.add(Q.move.name, this.handleMove, {
      passive: !1
    }), this.listeners.add(Q.end.name, this.handleEnd), this.windowListeners.add(TZ.Resize, this.handleCancel), this.windowListeners.add(TZ.DragStart, Xk), this.windowListeners.add(TZ.VisibilityChange, this.handleCancel), this.windowListeners.add(TZ.ContextMenu, Xk), this.documentListeners.add(TZ.Keydown, this.handleKeydown), J) {
      if (Y != null && Y({
        event: this.props.event,
        activeNode: this.props.activeNode,
        options: this.props.options
      }))
        return this.handleStart();
      if ($k(J)) {
        this.timeoutId = setTimeout(this.handleStart, J.delay);
        return;
      }
      if (Jk(J))
        return;
    }
    this.handleStart();
  }
  detach() {
    if (this.listeners.removeAll(), this.windowListeners.removeAll(), setTimeout(this.documentListeners.removeAll, 50), this.timeoutId !== null)
      clearTimeout(this.timeoutId), this.timeoutId = null;
  }
  handleStart() {
    let {
      initialCoordinates: Q
    } = this, {
      onStart: J
    } = this.props;
    if (Q)
      this.activated = !0, this.documentListeners.add(TZ.Click, ay, {
        capture: !0
      }), this.removeTextSelection(), this.documentListeners.add(TZ.SelectionChange, this.removeTextSelection), J(Q);
  }
  handleMove(Q) {
    var J;
    let {
      activated: Y,
      initialCoordinates: W,
      props: K
    } = this, {
      onMove: z,
      options: {
        activationConstraint: N
      }
    } = K;
    if (!W)
      return;
    let F = (J = XK(Q)) != null ? J : zX, L = b$(W, F);
    if (!Y && N) {
      if (Jk(N)) {
        if (N.tolerance != null && lE(L, N.tolerance))
          return this.handleCancel();
        if (lE(L, N.distance))
          return this.handleStart();
      }
      if ($k(N)) {
        if (lE(L, N.tolerance))
          return this.handleCancel();
      }
      return;
    }
    if (Q.cancelable)
      Q.preventDefault();
    z(F);
  }
  handleEnd() {
    let {
      onEnd: Q
    } = this.props;
    this.detach(), Q();
  }
  handleCancel() {
    let {
      onCancel: Q
    } = this.props;
    this.detach(), Q();
  }
  handleKeydown(Q) {
    if (Q.code === M1.Esc)
      this.handleCancel();
  }
  removeTextSelection() {
    var Q;
    (Q = this.document.getSelection()) == null || Q.removeAllRanges();
  }
}
var iy = {
  move: {
    name: "pointermove"
  },
  end: {
    name: "pointerup"
  }
};

class d$ extends oH {
  constructor(Q) {
    let {
      event: J
    } = Q, Y = y$(J.target);
    super(Q, iy, Y);
  }
}
d$.activators = [{
  eventName: "onPointerDown",
  handler: (Q, J) => {
    let {
      nativeEvent: Y
    } = Q, {
      onActivation: W
    } = J;
    if (!Y.isPrimary || Y.button !== 0)
      return !1;
    return W == null || W({
      event: Y
    }), !0;
  }
}];
var ty = {
  move: {
    name: "mousemove"
  },
  end: {
    name: "mouseup"
  }
}, aE;
(function(Q) {
  Q[Q.RightClick = 2] = "RightClick";
})(aE || (aE = {}));

class kk extends oH {
  constructor(Q) {
    super(Q, ty, y$(Q.event.target));
  }
}
kk.activators = [{
  eventName: "onMouseDown",
  handler: (Q, J) => {
    let {
      nativeEvent: Y
    } = Q, {
      onActivation: W
    } = J;
    if (Y.button === aE.RightClick)
      return !1;
    return W == null || W({
      event: Y
    }), !0;
  }
}];
var nE = {
  move: {
    name: "touchmove"
  },
  end: {
    name: "touchend"
  }
};

class Rk extends oH {
  constructor(Q) {
    super(Q, nE);
  }
  static setup() {
    return window.addEventListener(nE.move.name, Q, {
      capture: !1,
      passive: !1
    }), function J() {
      window.removeEventListener(nE.move.name, Q);
    };
    function Q() {}
  }
}
Rk.activators = [{
  eventName: "onTouchStart",
  handler: (Q, J) => {
    let {
      nativeEvent: Y
    } = Q, {
      onActivation: W
    } = J, {
      touches: K
    } = Y;
    if (K.length > 1)
      return !1;
    return W == null || W({
      event: Y
    }), !0;
  }
}];
var JK;
(function(Q) {
  Q[Q.Pointer = 0] = "Pointer", Q[Q.DraggableRect = 1] = "DraggableRect";
})(JK || (JK = {}));
var lH;
(function(Q) {
  Q[Q.TreeOrder = 0] = "TreeOrder", Q[Q.ReversedTreeOrder = 1] = "ReversedTreeOrder";
})(lH || (lH = {}));
function ey(Q) {
  let {
    acceleration: J,
    activator: Y = JK.Pointer,
    canScroll: W,
    draggingRect: K,
    enabled: z,
    interval: N = 5,
    order: F = lH.TreeOrder,
    pointerCoordinates: L,
    scrollableAncestors: w,
    scrollableAncestorRects: D,
    delta: R,
    threshold: V
  } = Q, g = Zf({
    delta: R,
    disabled: !z
  }), [s, i] = oD(), F0 = u.useRef({
    x: 0,
    y: 0
  }), r = u.useRef({
    x: 0,
    y: 0
  }), J0 = u.useMemo(() => {
    switch (Y) {
      case JK.Pointer:
        return L ? {
          top: L.y,
          bottom: L.y,
          left: L.x,
          right: L.x
        } : null;
      case JK.DraggableRect:
        return K;
    }
  }, [Y, K, L]), l = u.useRef(null), t = u.useCallback(() => {
    let M0 = l.current;
    if (!M0)
      return;
    let c0 = F0.current.x * r.current.x, I0 = F0.current.y * r.current.y;
    M0.scrollBy(c0, I0);
  }, []), $0 = u.useMemo(() => F === lH.TreeOrder ? [...w].reverse() : w, [F, w]);
  u.useEffect(() => {
    if (!z || !w.length || !J0) {
      i();
      return;
    }
    for (let M0 of $0) {
      if ((W == null ? void 0 : W(M0)) === !1)
        continue;
      let c0 = w.indexOf(M0), I0 = D[c0];
      if (!I0)
        continue;
      let {
        direction: p,
        speed: o
      } = py(M0, I0, J0, J, V);
      for (let Y0 of ["x", "y"])
        if (!g[Y0][p[Y0]])
          o[Y0] = 0, p[Y0] = 0;
      if (o.x > 0 || o.y > 0) {
        i(), l.current = M0, s(t, N), F0.current = o, r.current = p;
        return;
      }
    }
    F0.current = {
      x: 0,
      y: 0
    }, r.current = {
      x: 0,
      y: 0
    }, i();
  }, [
    J,
    t,
    W,
    i,
    z,
    N,
    JSON.stringify(J0),
    JSON.stringify(g),
    s,
    w,
    $0,
    D,
    JSON.stringify(V)
  ]);
}
var Qf = {
  x: {
    [M8.Backward]: !1,
    [M8.Forward]: !1
  },
  y: {
    [M8.Backward]: !1,
    [M8.Forward]: !1
  }
};
function Zf(Q) {
  let {
    delta: J,
    disabled: Y
  } = Q, W = ZK(J);
  return Bq((K) => {
    if (Y || !W || !K)
      return Qf;
    let z = {
      x: Math.sign(J.x - W.x),
      y: Math.sign(J.y - W.y)
    };
    return {
      x: {
        [M8.Backward]: K.x[M8.Backward] || z.x === -1,
        [M8.Forward]: K.x[M8.Forward] || z.x === 1
      },
      y: {
        [M8.Backward]: K.y[M8.Backward] || z.y === -1,
        [M8.Forward]: K.y[M8.Forward] || z.y === 1
      }
    };
  }, [Y, J, W]);
}
function Xf(Q, J) {
  let Y = J !== null ? Q.get(J) : void 0, W = Y ? Y.node.current : null;
  return Bq((K) => {
    var z;
    if (J === null)
      return null;
    return (z = W != null ? W : K) != null ? z : null;
  }, [W, J]);
}
function Jf(Q, J) {
  return u.useMemo(() => Q.reduce((Y, W) => {
    let {
      sensor: K
    } = W, z = K.activators.map((N) => ({
      eventName: N.eventName,
      handler: J(N.handler, W)
    }));
    return [...Y, ...z];
  }, []), [Q, J]);
}
var $K;
(function(Q) {
  Q[Q.Always = 0] = "Always", Q[Q.BeforeDragging = 1] = "BeforeDragging", Q[Q.WhileDragging = 2] = "WhileDragging";
})($K || ($K = {}));
var rE;
(function(Q) {
  Q.Optimized = "optimized";
})(rE || (rE = {}));
var Yk = /* @__PURE__ */ new Map;
function $f(Q, J) {
  let {
    dragging: Y,
    dependencies: W,
    config: K
  } = J, [z, N] = u.useState(null), {
    frequency: F,
    measure: L,
    strategy: w
  } = K, D = u.useRef(Q), R = F0(), V = jq(R), g = u.useCallback(function(r) {
    if (r === void 0)
      r = [];
    if (V.current)
      return;
    N((J0) => {
      if (J0 === null)
        return r;
      return J0.concat(r.filter((l) => !J0.includes(l)));
    });
  }, [V]), s = u.useRef(null), i = Bq((r) => {
    if (R && !Y)
      return Yk;
    if (!r || r === Yk || D.current !== Q || z != null) {
      let J0 = /* @__PURE__ */ new Map;
      for (let l of Q) {
        if (!l)
          continue;
        if (z && z.length > 0 && !z.includes(l.id) && l.rect.current) {
          J0.set(l.id, l.rect.current);
          continue;
        }
        let t = l.node.current, $0 = t ? new sH(L(t), t) : null;
        if (l.rect.current = $0, $0)
          J0.set(l.id, $0);
      }
      return J0;
    }
    return r;
  }, [Q, z, Y, R, L]);
  return u.useEffect(() => {
    D.current = Q;
  }, [Q]), u.useEffect(() => {
    if (R)
      return;
    g();
  }, [Y, R]), u.useEffect(() => {
    if (z && z.length > 0)
      N(null);
  }, [JSON.stringify(z)]), u.useEffect(() => {
    if (R || typeof F !== "number" || s.current !== null)
      return;
    s.current = setTimeout(() => {
      g(), s.current = null;
    }, F);
  }, [F, R, g, ...W]), {
    droppableRects: i,
    measureDroppableContainers: g,
    measuringScheduled: z != null
  };
  function F0() {
    switch (w) {
      case $K.Always:
        return !1;
      case $K.BeforeDragging:
        return Y;
      default:
        return !Y;
    }
  }
}
function tE(Q, J) {
  return Bq((Y) => {
    if (!Q)
      return null;
    if (Y)
      return Y;
    return typeof J === "function" ? J(Q) : Q;
  }, [J, Q]);
}
function Yf(Q, J) {
  return tE(Q, J);
}
function qf(Q) {
  let {
    callback: J,
    disabled: Y
  } = Q, W = e3(J), K = u.useMemo(() => {
    if (Y || typeof window === "undefined" || typeof window.MutationObserver === "undefined")
      return;
    let {
      MutationObserver: z
    } = window;
    return new z(W);
  }, [W, Y]);
  return u.useEffect(() => {
    return () => K == null ? void 0 : K.disconnect();
  }, [K]), K;
}
function aH(Q) {
  let {
    callback: J,
    disabled: Y
  } = Q, W = e3(J), K = u.useMemo(() => {
    if (Y || typeof window === "undefined" || typeof window.ResizeObserver === "undefined")
      return;
    let {
      ResizeObserver: z
    } = window;
    return new z(W);
  }, [Y]);
  return u.useEffect(() => {
    return () => K == null ? void 0 : K.disconnect();
  }, [K]), K;
}
function Wf(Q) {
  return new sH(c$(Q), Q);
}
function qk(Q, J, Y) {
  if (J === void 0)
    J = Wf;
  let [W, K] = u.useReducer(F, null), z = qf({
    callback(L) {
      if (!Q)
        return;
      for (let w of L) {
        let {
          type: D,
          target: R
        } = w;
        if (D === "childList" && R instanceof HTMLElement && R.contains(Q)) {
          K();
          break;
        }
      }
    }
  }), N = aH({
    callback: K
  });
  return cQ(() => {
    if (K(), Q)
      N == null || N.observe(Q), z == null || z.observe(document.body, {
        childList: !0,
        subtree: !0
      });
    else
      N == null || N.disconnect(), z == null || z.disconnect();
  }, [Q]), W;
  function F(L) {
    if (!Q)
      return null;
    if (Q.isConnected === !1) {
      var w;
      return (w = L != null ? L : Y) != null ? w : null;
    }
    let D = J(Q);
    if (JSON.stringify(L) === JSON.stringify(D))
      return L;
    return D;
  }
}
function Kf(Q) {
  let J = tE(Q);
  return Ek(Q, J);
}
var Wk = [];
function Hf(Q) {
  let J = u.useRef(Q), Y = Bq((W) => {
    if (!Q)
      return Wk;
    if (W && W !== Wk && Q && J.current && Q.parentNode === J.current.parentNode)
      return W;
    return YK(Q);
  }, [Q]);
  return u.useEffect(() => {
    J.current = Q;
  }, [Q]), Y;
}
function Gf(Q) {
  let [J, Y] = u.useState(null), W = u.useRef(Q), K = u.useCallback((z) => {
    let N = dE(z.target);
    if (!N)
      return;
    Y((F) => {
      if (!F)
        return null;
      return F.set(N, oE(N)), new Map(F);
    });
  }, []);
  return u.useEffect(() => {
    let z = W.current;
    if (Q !== z) {
      N(z);
      let F = Q.map((L) => {
        let w = dE(L);
        if (w)
          return w.addEventListener("scroll", K, {
            passive: !0
          }), [w, oE(w)];
        return null;
      }).filter((L) => L != null);
      Y(F.length ? new Map(F) : null), W.current = Q;
    }
    return () => {
      N(Q), N(z);
    };
    function N(F) {
      F.forEach((L) => {
        let w = dE(L);
        w == null || w.removeEventListener("scroll", K);
      });
    }
  }, [K, Q]), u.useMemo(() => {
    if (Q.length)
      return J ? Array.from(J.values()).reduce((z, N) => m$(z, N), zX) : wk(Q);
    return zX;
  }, [Q, J]);
}
function Kk(Q, J) {
  if (J === void 0)
    J = [];
  let Y = u.useRef(null);
  return u.useEffect(() => {
    Y.current = null;
  }, J), u.useEffect(() => {
    let W = Q !== zX;
    if (W && !Y.current)
      Y.current = Q;
    if (!W && Y.current)
      Y.current = null;
  }, [Q]), Y.current ? b$(Q, Y.current) : zX;
}
function zf(Q) {
  u.useEffect(() => {
    if (!t3)
      return;
    let J = Q.map((Y) => {
      let {
        sensor: W
      } = Y;
      return W.setup == null ? void 0 : W.setup();
    });
    return () => {
      for (let Y of J)
        Y == null || Y();
    };
  }, Q.map((J) => {
    let {
      sensor: Y
    } = J;
    return Y;
  }));
}
function Nf(Q, J) {
  return u.useMemo(() => {
    return Q.reduce((Y, W) => {
      let {
        eventName: K,
        handler: z
      } = W;
      return Y[K] = (N) => {
        z(N, J);
      }, Y;
    }, {});
  }, [Q, J]);
}
function jk(Q) {
  return u.useMemo(() => Q ? my(Q) : null, [Q]);
}
var sE = [];
function Ef(Q, J) {
  if (J === void 0)
    J = c$;
  let [Y] = Q, W = jk(Y ? YQ(Y) : null), [K, z] = u.useReducer(F, sE), N = aH({
    callback: z
  });
  if (Q.length > 0 && K === sE)
    z();
  return cQ(() => {
    if (Q.length)
      Q.forEach((L) => N == null ? void 0 : N.observe(L));
    else
      N == null || N.disconnect(), z();
  }, [Q]), K;
  function F() {
    if (!Q.length)
      return sE;
    return Q.map((L) => Lk(L) ? W : new sH(J(L), L));
  }
}
function Bk(Q) {
  if (!Q)
    return null;
  if (Q.children.length > 1)
    return Q;
  let J = Q.children[0];
  return Rq(J) ? J : Q;
}
function Ff(Q) {
  let {
    measure: J
  } = Q, [Y, W] = u.useState(null), K = u.useCallback((w) => {
    for (let {
      target: D
    } of w)
      if (Rq(D)) {
        W((R) => {
          let V = J(D);
          return R ? {
            ...R,
            width: V.width,
            height: V.height
          } : V;
        });
        break;
      }
  }, [J]), z = aH({
    callback: K
  }), N = u.useCallback((w) => {
    let D = Bk(w);
    if (z == null || z.disconnect(), D)
      z == null || z.observe(D);
    W(D ? J(D) : null);
  }, [J, z]), [F, L] = QK(N);
  return u.useMemo(() => ({
    nodeRef: F,
    rect: Y,
    setRef: L
  }), [Y, F, L]);
}
var Uf = [{
  sensor: d$,
  options: {}
}, {
  sensor: p$,
  options: {}
}], Pf = {
  current: {}
}, pH = {
  draggable: {
    measure: Zk
  },
  droppable: {
    measure: Zk,
    strategy: $K.WhileDragging,
    frequency: rE.Optimized
  },
  dragOverlay: {
    measure: c$
  }
};

class Sq extends Map {
  get(Q) {
    var J;
    return Q != null ? (J = super.get(Q)) != null ? J : void 0 : void 0;
  }
  toArray() {
    return Array.from(this.values());
  }
  getEnabled() {
    return this.toArray().filter((Q) => {
      let {
        disabled: J
      } = Q;
      return !J;
    });
  }
  getNodeFor(Q) {
    var J, Y;
    return (J = (Y = this.get(Q)) == null ? void 0 : Y.node.current) != null ? J : void 0;
  }
}
var Af = {
  activatorEvent: null,
  active: null,
  activeNode: null,
  activeNodeRect: null,
  collisions: null,
  containerNodeRect: null,
  draggableNodes: /* @__PURE__ */ new Map,
  droppableRects: /* @__PURE__ */ new Map,
  droppableContainers: /* @__PURE__ */ new Sq,
  over: null,
  dragOverlay: {
    nodeRef: {
      current: null
    },
    rect: null,
    setRef: dH
  },
  scrollableAncestors: [],
  scrollableAncestorRects: [],
  measuringConfiguration: pH,
  measureDroppableContainers: dH,
  windowRect: null,
  measuringScheduled: !1
}, Ck = {
  activatorEvent: null,
  activators: [],
  active: null,
  activeNodeRect: null,
  ariaDescribedById: {
    draggable: ""
  },
  dispatch: dH,
  draggableNodes: /* @__PURE__ */ new Map,
  over: null,
  measureDroppableContainers: dH
}, qK = /* @__PURE__ */ u.createContext(Ck), Vk = /* @__PURE__ */ u.createContext(Af);
function Lf() {
  return {
    draggable: {
      active: null,
      initialCoordinates: {
        x: 0,
        y: 0
      },
      nodes: /* @__PURE__ */ new Map,
      translate: {
        x: 0,
        y: 0
      }
    },
    droppable: {
      containers: new Sq
    }
  };
}
function Of(Q, J) {
  switch (J.type) {
    case Y8.DragStart:
      return {
        ...Q,
        draggable: {
          ...Q.draggable,
          initialCoordinates: J.initialCoordinates,
          active: J.active
        }
      };
    case Y8.DragMove:
      if (!Q.draggable.active)
        return Q;
      return {
        ...Q,
        draggable: {
          ...Q.draggable,
          translate: {
            x: J.coordinates.x - Q.draggable.initialCoordinates.x,
            y: J.coordinates.y - Q.draggable.initialCoordinates.y
          }
        }
      };
    case Y8.DragEnd:
    case Y8.DragCancel:
      return {
        ...Q,
        draggable: {
          ...Q.draggable,
          active: null,
          initialCoordinates: {
            x: 0,
            y: 0
          },
          translate: {
            x: 0,
            y: 0
          }
        }
      };
    case Y8.RegisterDroppable: {
      let {
        element: Y
      } = J, {
        id: W
      } = Y, K = new Sq(Q.droppable.containers);
      return K.set(W, Y), {
        ...Q,
        droppable: {
          ...Q.droppable,
          containers: K
        }
      };
    }
    case Y8.SetDroppableDisabled: {
      let {
        id: Y,
        key: W,
        disabled: K
      } = J, z = Q.droppable.containers.get(Y);
      if (!z || W !== z.key)
        return Q;
      let N = new Sq(Q.droppable.containers);
      return N.set(Y, {
        ...z,
        disabled: K
      }), {
        ...Q,
        droppable: {
          ...Q.droppable,
          containers: N
        }
      };
    }
    case Y8.UnregisterDroppable: {
      let {
        id: Y,
        key: W
      } = J, K = Q.droppable.containers.get(Y);
      if (!K || W !== K.key)
        return Q;
      let z = new Sq(Q.droppable.containers);
      return z.delete(Y), {
        ...Q,
        droppable: {
          ...Q.droppable,
          containers: z
        }
      };
    }
    default:
      return Q;
  }
}
function wf(Q) {
  let {
    disabled: J
  } = Q, {
    active: Y,
    activatorEvent: W,
    draggableNodes: K
  } = u.useContext(qK), z = ZK(W), N = ZK(Y == null ? void 0 : Y.id);
  return u.useEffect(() => {
    if (J)
      return;
    if (!W && z && N != null) {
      if (!Cq(z))
        return;
      if (document.activeElement === z.target)
        return;
      let F = K.get(N);
      if (!F)
        return;
      let {
        activatorNode: L,
        node: w
      } = F;
      if (!L.current && !w.current)
        return;
      requestAnimationFrame(() => {
        for (let D of [L.current, w.current]) {
          if (!D)
            continue;
          let R = rD(D);
          if (R) {
            R.focus();
            break;
          }
        }
      });
    }
  }, [W, J, K, N, z]), null;
}
function Sk(Q, J) {
  let {
    transform: Y,
    ...W
  } = J;
  return Q != null && Q.length ? Q.reduce((K, z) => {
    return z({
      transform: K,
      ...W
    });
  }, Y) : Y;
}
function Mf(Q) {
  return u.useMemo(() => ({
    draggable: {
      ...pH.draggable,
      ...Q == null ? void 0 : Q.draggable
    },
    droppable: {
      ...pH.droppable,
      ...Q == null ? void 0 : Q.droppable
    },
    dragOverlay: {
      ...pH.dragOverlay,
      ...Q == null ? void 0 : Q.dragOverlay
    }
  }), [Q == null ? void 0 : Q.draggable, Q == null ? void 0 : Q.droppable, Q == null ? void 0 : Q.dragOverlay]);
}
function Df(Q) {
  let {
    activeNode: J,
    measure: Y,
    initialRect: W,
    config: K = !0
  } = Q, z = u.useRef(!1), {
    x: N,
    y: F
  } = typeof K === "boolean" ? {
    x: K,
    y: K
  } : K;
  cQ(() => {
    if (!N && !F || !J) {
      z.current = !1;
      return;
    }
    if (z.current || !W)
      return;
    let w = J == null ? void 0 : J.node.current;
    if (!w || w.isConnected === !1)
      return;
    let D = Y(w), R = Ek(D, W);
    if (!N)
      R.x = 0;
    if (!F)
      R.y = 0;
    if (z.current = !0, Math.abs(R.x) > 0 || Math.abs(R.y) > 0) {
      let V = Uk(w);
      if (V)
        V.scrollBy({
          top: R.y,
          left: R.x
        });
    }
  }, [J, N, F, W, Y]);
}
var rH = /* @__PURE__ */ u.createContext({
  ...zX,
  scaleX: 1,
  scaleY: 1
}), yJ;
(function(Q) {
  Q[Q.Uninitialized = 0] = "Uninitialized", Q[Q.Initializing = 1] = "Initializing", Q[Q.Initialized = 2] = "Initialized";
})(yJ || (yJ = {}));
var iH = /* @__PURE__ */ u.memo(function Q(J) {
  var Y, W, K, z;
  let {
    id: N,
    accessibility: F,
    autoScroll: L = !0,
    children: w,
    sensors: D = Uf,
    collisionDetection: R = gy,
    measuring: V,
    modifiers: g,
    ...s
  } = J, i = u.useReducer(Of, void 0, Lf), [F0, r] = i, [J0, l] = Ry(), [t, $0] = u.useState(yJ.Uninitialized), M0 = t === yJ.Initialized, {
    draggable: {
      active: c0,
      nodes: I0,
      translate: p
    },
    droppable: {
      containers: o
    }
  } = F0, Y0 = c0 ? I0.get(c0) : null, A0 = u.useRef({
    initial: null,
    translated: null
  }), P0 = u.useMemo(() => {
    var t1;
    return c0 != null ? {
      id: c0,
      data: (t1 = Y0 == null ? void 0 : Y0.data) != null ? t1 : Pf,
      rect: A0
    } : null;
  }, [c0, Y0]), Y1 = u.useRef(null), [N0, W0] = u.useState(null), [v0, n1] = u.useState(null), g1 = jq(s, Object.values(s)), s1 = f$("DndDescribedBy", N), _1 = u.useMemo(() => o.getEnabled(), [o]), U1 = Mf(V), {
    droppableRects: x0,
    measureDroppableContainers: N6,
    measuringScheduled: C6
  } = $f(_1, {
    dragging: M0,
    dependencies: [p.x, p.y],
    config: U1.droppable
  }), o1 = Xf(I0, c0), f1 = u.useMemo(() => v0 ? XK(v0) : null, [v0]), E6 = y1(), x1 = Yf(o1, U1.draggable.measure);
  Df({
    activeNode: c0 ? I0.get(c0) : null,
    config: E6.layoutShiftCompensation,
    initialRect: x1,
    measure: U1.draggable.measure
  });
  let l0 = qk(o1, U1.draggable.measure, x1), i1 = qk(o1 ? o1.parentElement : null), Z0 = u.useRef({
    activatorEvent: null,
    active: null,
    activeNode: o1,
    collisionRect: null,
    collisions: null,
    droppableRects: x0,
    draggableNodes: I0,
    draggingNode: null,
    draggingNodeRect: null,
    droppableContainers: o,
    over: null,
    scrollableAncestors: [],
    scrollAdjustedTranslate: null
  }), F6 = o.getNodeFor((Y = Z0.current.over) == null ? void 0 : Y.id), C1 = Ff({
    measure: U1.dragOverlay.measure
  }), v1 = (W = C1.nodeRef.current) != null ? W : o1, h6 = M0 ? (K = C1.rect) != null ? K : l0 : null, c8 = Boolean(C1.nodeRef.current && C1.rect), p6 = Kf(c8 ? null : l0), k8 = jk(v1 ? YQ(v1) : null), q8 = Hf(M0 ? F6 != null ? F6 : o1 : null), W8 = Ef(q8), d6 = Sk(g, {
    transform: {
      x: p.x - p6.x,
      y: p.y - p6.y,
      scaleX: 1,
      scaleY: 1
    },
    activatorEvent: v0,
    active: P0,
    activeNodeRect: l0,
    containerNodeRect: i1,
    draggingNodeRect: h6,
    over: Z0.current.over,
    overlayNodeRect: C1.rect,
    scrollableAncestors: q8,
    scrollableAncestorRects: W8,
    windowRect: k8
  }), A6 = f1 ? m$(f1, p) : null, RQ = Gf(q8), R8 = Kk(RQ), WQ = Kk(RQ, [l0]), l6 = m$(d6, R8), p8 = h6 ? hy(h6, d6) : null, d8 = P0 && p8 ? R({
    active: P0,
    collisionRect: p8,
    droppableRects: x0,
    droppableContainers: _1,
    pointerCoordinates: A6
  }) : null, jQ = iE(d8, "id"), [Q0, D0] = u.useState(null), f0 = c8 ? d6 : m$(d6, WQ), k1 = xy(f0, (z = Q0 == null ? void 0 : Q0.rect) != null ? z : null, l0), h1 = u.useCallback((t1, X6) => {
    let {
      sensor: L6,
      options: n8
    } = X6;
    if (Y1.current == null)
      return;
    let K8 = I0.get(Y1.current);
    if (!K8)
      return;
    let H8 = t1.nativeEvent, j8 = new L6({
      active: Y1.current,
      activeNode: K8,
      event: H8,
      options: n8,
      context: Z0,
      onStart(y6) {
        let BQ = Y1.current;
        if (BQ == null)
          return;
        let s8 = I0.get(BQ);
        if (!s8)
          return;
        let {
          onDragStart: o8
        } = g1.current, KQ = {
          active: {
            id: BQ,
            data: s8.data,
            rect: A0
          }
        };
        fJ.unstable_batchedUpdates(() => {
          o8 == null || o8(KQ), $0(yJ.Initializing), r({
            type: Y8.DragStart,
            initialCoordinates: y6,
            active: BQ
          }), J0({
            type: "onDragStart",
            event: KQ
          });
        });
      },
      onMove(y6) {
        r({
          type: Y8.DragMove,
          coordinates: y6
        });
      },
      onEnd: G8(Y8.DragEnd),
      onCancel: G8(Y8.DragCancel)
    });
    fJ.unstable_batchedUpdates(() => {
      W0(j8), n1(t1.nativeEvent);
    });
    function G8(y6) {
      return async function BQ() {
        let {
          active: s8,
          collisions: o8,
          over: KQ,
          scrollAdjustedTranslate: PX
        } = Z0.current, pQ = null;
        if (s8 && PX) {
          let {
            cancelDrop: HQ
          } = g1.current;
          if (pQ = {
            activatorEvent: H8,
            active: s8,
            collisions: o8,
            delta: PX,
            over: KQ
          }, y6 === Y8.DragEnd && typeof HQ === "function") {
            if (await Promise.resolve(HQ(pQ)))
              y6 = Y8.DragCancel;
          }
        }
        Y1.current = null, fJ.unstable_batchedUpdates(() => {
          r({
            type: y6
          }), $0(yJ.Uninitialized), D0(null), W0(null), n1(null);
          let HQ = y6 === Y8.DragEnd ? "onDragEnd" : "onDragCancel";
          if (pQ) {
            let fZ = g1.current[HQ];
            fZ == null || fZ(pQ), J0({
              type: HQ,
              event: pQ
            });
          }
        });
      };
    }
  }, [I0]), V6 = u.useCallback((t1, X6) => {
    return (L6, n8) => {
      let K8 = L6.nativeEvent, H8 = I0.get(n8);
      if (Y1.current !== null || !H8 || K8.dndKit || K8.defaultPrevented)
        return;
      let j8 = {
        active: H8
      };
      if (t1(L6, X6.options, j8) === !0)
        K8.dndKit = {
          capturedBy: X6.sensor
        }, Y1.current = n8, h1(L6, X6);
    };
  }, [I0, h1]), a1 = Jf(D, V6);
  zf(D), cQ(() => {
    if (l0 && t === yJ.Initializing)
      $0(yJ.Initialized);
  }, [l0, t]), u.useEffect(() => {
    let {
      onDragMove: t1
    } = g1.current, {
      active: X6,
      activatorEvent: L6,
      collisions: n8,
      over: K8
    } = Z0.current;
    if (!X6 || !L6)
      return;
    let H8 = {
      active: X6,
      activatorEvent: L6,
      collisions: n8,
      delta: {
        x: l6.x,
        y: l6.y
      },
      over: K8
    };
    fJ.unstable_batchedUpdates(() => {
      t1 == null || t1(H8), J0({
        type: "onDragMove",
        event: H8
      });
    });
  }, [l6.x, l6.y]), u.useEffect(() => {
    let {
      active: t1,
      activatorEvent: X6,
      collisions: L6,
      droppableContainers: n8,
      scrollAdjustedTranslate: K8
    } = Z0.current;
    if (!t1 || Y1.current == null || !X6 || !K8)
      return;
    let {
      onDragOver: H8
    } = g1.current, j8 = n8.get(jQ), G8 = j8 && j8.rect.current ? {
      id: j8.id,
      rect: j8.rect.current,
      data: j8.data,
      disabled: j8.disabled
    } : null, y6 = {
      active: t1,
      activatorEvent: X6,
      collisions: L6,
      delta: {
        x: K8.x,
        y: K8.y
      },
      over: G8
    };
    fJ.unstable_batchedUpdates(() => {
      D0(G8), H8 == null || H8(y6), J0({
        type: "onDragOver",
        event: y6
      });
    });
  }, [jQ]), cQ(() => {
    Z0.current = {
      activatorEvent: v0,
      active: P0,
      activeNode: o1,
      collisionRect: p8,
      collisions: d8,
      droppableRects: x0,
      draggableNodes: I0,
      draggingNode: v1,
      draggingNodeRect: h6,
      droppableContainers: o,
      over: Q0,
      scrollableAncestors: q8,
      scrollAdjustedTranslate: l6
    }, A0.current = {
      initial: h6,
      translated: p8
    };
  }, [P0, o1, d8, p8, I0, v1, h6, x0, o, Q0, q8, l6]), ey({
    ...E6,
    delta: p,
    draggingRect: p8,
    pointerCoordinates: A6,
    scrollableAncestors: q8,
    scrollableAncestorRects: W8
  });
  let l8 = u.useMemo(() => {
    return {
      active: P0,
      activeNode: o1,
      activeNodeRect: l0,
      activatorEvent: v0,
      collisions: d8,
      containerNodeRect: i1,
      dragOverlay: C1,
      draggableNodes: I0,
      droppableContainers: o,
      droppableRects: x0,
      over: Q0,
      measureDroppableContainers: N6,
      scrollableAncestors: q8,
      scrollableAncestorRects: W8,
      measuringConfiguration: U1,
      measuringScheduled: C6,
      windowRect: k8
    };
  }, [P0, o1, l0, v0, d8, i1, C1, I0, o, x0, Q0, N6, q8, W8, U1, C6, k8]), W1 = u.useMemo(() => {
    return {
      activatorEvent: v0,
      activators: a1,
      active: P0,
      activeNodeRect: l0,
      ariaDescribedById: {
        draggable: s1
      },
      dispatch: r,
      draggableNodes: I0,
      over: Q0,
      measureDroppableContainers: N6
    };
  }, [v0, a1, P0, l0, r, s1, I0, Q0, N6]);
  return u.default.createElement(zk.Provider, {
    value: l
  }, u.default.createElement(qK.Provider, {
    value: W1
  }, u.default.createElement(Vk.Provider, {
    value: l8
  }, u.default.createElement(rH.Provider, {
    value: k1
  }, w)), u.default.createElement(wf, {
    disabled: (F == null ? void 0 : F.restoreFocus) === !1
  })), u.default.createElement(Cy, {
    ...F,
    hiddenTextDescribedById: s1
  }));
  function y1() {
    let t1 = (N0 == null ? void 0 : N0.autoScrollEnabled) === !1, X6 = typeof L === "object" ? L.enabled === !1 : L === !1, L6 = M0 && !t1 && !X6;
    if (typeof L === "object")
      return {
        ...L,
        enabled: L6
      };
    return {
      enabled: L6
    };
  }
}), kf = /* @__PURE__ */ u.createContext(null), Hk = "button", Rf = "Droppable";
function Ik(Q) {
  let {
    id: J,
    data: Y,
    disabled: W = !1,
    attributes: K
  } = Q, z = f$(Rf), {
    activators: N,
    activatorEvent: F,
    active: L,
    activeNodeRect: w,
    ariaDescribedById: D,
    draggableNodes: R,
    over: V
  } = u.useContext(qK), {
    role: g = Hk,
    roleDescription: s = "draggable",
    tabIndex: i = 0
  } = K != null ? K : {}, F0 = (L == null ? void 0 : L.id) === J, r = u.useContext(F0 ? rH : kf), [J0, l] = QK(), [t, $0] = QK(), M0 = Nf(N, J), c0 = jq(Y);
  cQ(() => {
    return R.set(J, {
      id: J,
      key: z,
      node: J0,
      activatorNode: t,
      data: c0
    }), () => {
      let p = R.get(J);
      if (p && p.key === z)
        R.delete(J);
    };
  }, [R, J]);
  let I0 = u.useMemo(() => ({
    role: g,
    tabIndex: i,
    "aria-disabled": W,
    "aria-pressed": F0 && g === Hk ? !0 : void 0,
    "aria-roledescription": s,
    "aria-describedby": D.draggable
  }), [W, g, i, F0, s, D.draggable]);
  return {
    active: L,
    activatorEvent: F,
    activeNodeRect: w,
    attributes: I0,
    isDragging: F0,
    listeners: W ? void 0 : M0,
    node: J0,
    over: V,
    setNodeRef: l,
    setActivatorNodeRef: $0,
    transform: r
  };
}
function eE() {
  return u.useContext(Vk);
}
var jf = "Droppable", Bf = {
  timeout: 25
};
function WK(Q) {
  let {
    data: J,
    disabled: Y = !1,
    id: W,
    resizeObserverConfig: K
  } = Q, z = f$(jf), {
    active: N,
    dispatch: F,
    over: L,
    measureDroppableContainers: w
  } = u.useContext(qK), D = u.useRef({
    disabled: Y
  }), R = u.useRef(!1), V = u.useRef(null), g = u.useRef(null), {
    disabled: s,
    updateMeasurementsFor: i,
    timeout: F0
  } = {
    ...Bf,
    ...K
  }, r = jq(i != null ? i : W), J0 = u.useCallback(() => {
    if (!R.current) {
      R.current = !0;
      return;
    }
    if (g.current != null)
      clearTimeout(g.current);
    g.current = setTimeout(() => {
      w(Array.isArray(r.current) ? r.current : [r.current]), g.current = null;
    }, F0);
  }, [F0]), l = aH({
    callback: J0,
    disabled: s || !N
  }), t = u.useCallback((I0, p) => {
    if (!l)
      return;
    if (p)
      l.unobserve(p), R.current = !1;
    if (I0)
      l.observe(I0);
  }, [l]), [$0, M0] = QK(t), c0 = jq(J);
  return u.useEffect(() => {
    if (!l || !$0.current)
      return;
    l.disconnect(), R.current = !1, l.observe($0.current);
  }, [$0, l]), cQ(() => {
    return F({
      type: Y8.RegisterDroppable,
      element: {
        id: W,
        key: z,
        disabled: Y,
        node: $0,
        rect: V,
        data: c0
      }
    }), () => F({
      type: Y8.UnregisterDroppable,
      key: z,
      id: W
    });
  }, [W]), u.useEffect(() => {
    if (Y !== D.current.disabled)
      F({
        type: Y8.SetDroppableDisabled,
        id: W,
        key: z,
        disabled: Y
      }), D.current.disabled = Y;
  }, [W, z, Y, F]), {
    active: N,
    rect: V,
    isOver: (L == null ? void 0 : L.id) === W,
    node: $0,
    over: L,
    setNodeRef: M0
  };
}
function Cf(Q) {
  let {
    animation: J,
    children: Y
  } = Q, [W, K] = u.useState(null), [z, N] = u.useState(null), F = ZK(Y);
  if (!Y && !W && F)
    K(F);
  return cQ(() => {
    if (!z)
      return;
    let L = W == null ? void 0 : W.key, w = W == null ? void 0 : W.props.id;
    if (L == null || w == null) {
      K(null);
      return;
    }
    Promise.resolve(J(w, z)).then(() => {
      K(null);
    });
  }, [J, W, z]), u.default.createElement(u.default.Fragment, null, Y, W ? u.cloneElement(W, {
    ref: N
  }) : null);
}
var Vf = {
  x: 0,
  y: 0,
  scaleX: 1,
  scaleY: 1
};
function Sf(Q) {
  let {
    children: J
  } = Q;
  return u.default.createElement(qK.Provider, {
    value: Ck
  }, u.default.createElement(rH.Provider, {
    value: Vf
  }, J));
}
var If = {
  position: "fixed",
  touchAction: "none"
}, _f = (Q) => {
  return Cq(Q) ? "transform 250ms ease" : void 0;
}, Tf = /* @__PURE__ */ u.forwardRef((Q, J) => {
  let {
    as: Y,
    activatorEvent: W,
    adjustScale: K,
    children: z,
    className: N,
    rect: F,
    style: L,
    transform: w,
    transition: D = _f
  } = Q;
  if (!F)
    return null;
  let R = K ? w : {
    ...w,
    scaleX: 1,
    scaleY: 1
  }, V = {
    ...If,
    width: F.width,
    height: F.height,
    top: F.top,
    left: F.left,
    transform: GX.Transform.toString(R),
    transformOrigin: K && W ? Sy(W, F) : void 0,
    transition: typeof D === "function" ? D(W) : D,
    ...L
  };
  return u.default.createElement(Y, {
    className: N,
    style: V,
    ref: J
  }, z);
}), QF = (Q) => (J) => {
  let {
    active: Y,
    dragOverlay: W
  } = J, K = {}, {
    styles: z,
    className: N
  } = Q;
  if (z != null && z.active)
    for (let [F, L] of Object.entries(z.active)) {
      if (L === void 0)
        continue;
      K[F] = Y.node.style.getPropertyValue(F), Y.node.style.setProperty(F, L);
    }
  if (z != null && z.dragOverlay)
    for (let [F, L] of Object.entries(z.dragOverlay)) {
      if (L === void 0)
        continue;
      W.node.style.setProperty(F, L);
    }
  if (N != null && N.active)
    Y.node.classList.add(N.active);
  if (N != null && N.dragOverlay)
    W.node.classList.add(N.dragOverlay);
  return function F() {
    for (let [L, w] of Object.entries(K))
      Y.node.style.setProperty(L, w);
    if (N != null && N.active)
      Y.node.classList.remove(N.active);
  };
}, gf = (Q) => {
  let {
    transform: {
      initial: J,
      final: Y
    }
  } = Q;
  return [{
    transform: GX.Transform.toString(J)
  }, {
    transform: GX.Transform.toString(Y)
  }];
}, xf = {
  duration: 250,
  easing: "ease",
  keyframes: gf,
  sideEffects: /* @__PURE__ */ QF({
    styles: {
      active: {
        opacity: "0"
      }
    }
  })
};
function vf(Q) {
  let {
    config: J,
    draggableNodes: Y,
    droppableContainers: W,
    measuringConfiguration: K
  } = Q;
  return e3((z, N) => {
    if (J === null)
      return;
    let F = Y.get(z);
    if (!F)
      return;
    let L = F.node.current;
    if (!L)
      return;
    let w = Bk(N);
    if (!w)
      return;
    let {
      transform: D
    } = YQ(N).getComputedStyle(N), R = Fk(D);
    if (!R)
      return;
    let V = typeof J === "function" ? J : hf(J);
    return Mk(L, K.draggable.measure), V({
      active: {
        id: z,
        data: F.data,
        node: L,
        rect: K.draggable.measure(L)
      },
      draggableNodes: Y,
      dragOverlay: {
        node: N,
        rect: K.dragOverlay.measure(w)
      },
      droppableContainers: W,
      measuringConfiguration: K,
      transform: R
    });
  });
}
function hf(Q) {
  let {
    duration: J,
    easing: Y,
    sideEffects: W,
    keyframes: K
  } = {
    ...xf,
    ...Q
  };
  return (z) => {
    let {
      active: N,
      dragOverlay: F,
      transform: L,
      ...w
    } = z;
    if (!J)
      return;
    let D = {
      x: F.rect.left - N.rect.left,
      y: F.rect.top - N.rect.top
    }, R = {
      scaleX: L.scaleX !== 1 ? N.rect.width * L.scaleX / F.rect.width : 1,
      scaleY: L.scaleY !== 1 ? N.rect.height * L.scaleY / F.rect.height : 1
    }, V = {
      x: L.x - D.x,
      y: L.y - D.y,
      ...R
    }, g = K({
      ...w,
      active: N,
      dragOverlay: F,
      transform: {
        initial: L,
        final: V
      }
    }), [s] = g, i = g[g.length - 1];
    if (JSON.stringify(s) === JSON.stringify(i))
      return;
    let F0 = W == null ? void 0 : W({
      active: N,
      dragOverlay: F,
      ...w
    }), r = F.node.animate(g, {
      duration: J,
      easing: Y,
      fill: "forwards"
    });
    return new Promise((J0) => {
      r.onfinish = () => {
        F0 == null || F0(), J0();
      };
    });
  };
}
var Gk = 0;
function yf(Q) {
  return u.useMemo(() => {
    if (Q == null)
      return;
    return Gk++, Gk;
  }, [Q]);
}
var _k = /* @__PURE__ */ u.default.memo((Q) => {
  let {
    adjustScale: J = !1,
    children: Y,
    dropAnimation: W,
    style: K,
    transition: z,
    modifiers: N,
    wrapperElement: F = "div",
    className: L,
    zIndex: w = 999
  } = Q, {
    activatorEvent: D,
    active: R,
    activeNodeRect: V,
    containerNodeRect: g,
    draggableNodes: s,
    droppableContainers: i,
    dragOverlay: F0,
    over: r,
    measuringConfiguration: J0,
    scrollableAncestors: l,
    scrollableAncestorRects: t,
    windowRect: $0
  } = eE(), M0 = u.useContext(rH), c0 = yf(R == null ? void 0 : R.id), I0 = Sk(N, {
    activatorEvent: D,
    active: R,
    activeNodeRect: V,
    containerNodeRect: g,
    draggingNodeRect: F0.rect,
    over: r,
    overlayNodeRect: F0.rect,
    scrollableAncestors: l,
    scrollableAncestorRects: t,
    transform: M0,
    windowRect: $0
  }), p = tE(V), o = vf({
    config: W,
    draggableNodes: s,
    droppableContainers: i,
    measuringConfiguration: J0
  }), Y0 = p ? F0.setRef : void 0;
  return u.default.createElement(Sf, null, u.default.createElement(Cf, {
    animation: o
  }, R && c0 ? u.default.createElement(Tf, {
    key: c0,
    id: R.id,
    ref: Y0,
    as: F,
    activatorEvent: D,
    adjustScale: J,
    className: L,
    transition: z,
    rect: p,
    style: {
      zIndex: w,
      ...K
    },
    transform: I0
  }, Y) : null));
});

// node_modules/@dnd-kit/sortable/dist/sortable.esm.js
var g6 = D6(LQ(), 1);
function _q(Q, J, Y) {
  let W = Q.slice();
  return W.splice(Y < 0 ? W.length + Y : Y, 0, W.splice(J, 1)[0]), W;
}
function ff(Q, J) {
  return Q.reduce((Y, W, K) => {
    let z = J.get(W);
    if (z)
      Y[K] = z;
    return Y;
  }, Array(Q.length));
}
function tH(Q) {
  return Q !== null && Q >= 0;
}
function mf(Q, J) {
  if (Q === J)
    return !0;
  if (Q.length !== J.length)
    return !1;
  for (let Y = 0;Y < Q.length; Y++)
    if (Q[Y] !== J[Y])
      return !1;
  return !0;
}
function bf(Q) {
  if (typeof Q === "boolean")
    return {
      draggable: Q,
      droppable: Q
    };
  return Q;
}
var Tk = (Q) => {
  let {
    rects: J,
    activeIndex: Y,
    overIndex: W,
    index: K
  } = Q, z = _q(J, W, Y), N = J[K], F = z[K];
  if (!F || !N)
    return null;
  return {
    x: F.left - N.left,
    y: F.top - N.top,
    scaleX: F.width / N.width,
    scaleY: F.height / N.height
  };
};
var gk = "Sortable", xk = /* @__PURE__ */ g6.default.createContext({
  activeIndex: -1,
  containerId: gk,
  disableTransforms: !1,
  items: [],
  overIndex: -1,
  useDragOverlay: !1,
  sortedRects: [],
  strategy: Tk,
  disabled: {
    draggable: !1,
    droppable: !1
  }
});
function KK(Q) {
  let {
    children: J,
    id: Y,
    items: W,
    strategy: K = Tk,
    disabled: z = !1
  } = Q, {
    active: N,
    dragOverlay: F,
    droppableRects: L,
    over: w,
    measureDroppableContainers: D
  } = eE(), R = f$(gk, Y), V = Boolean(F.rect !== null), g = g6.useMemo(() => W.map((M0) => typeof M0 === "object" && ("id" in M0) ? M0.id : M0), [W]), s = N != null, i = N ? g.indexOf(N.id) : -1, F0 = w ? g.indexOf(w.id) : -1, r = g6.useRef(g), J0 = !mf(g, r.current), l = F0 !== -1 && i === -1 || J0, t = bf(z);
  cQ(() => {
    if (J0 && s)
      D(g);
  }, [J0, g, s, D]), g6.useEffect(() => {
    r.current = g;
  }, [g]);
  let $0 = g6.useMemo(() => ({
    activeIndex: i,
    containerId: R,
    disabled: t,
    disableTransforms: l,
    items: g,
    overIndex: F0,
    useDragOverlay: V,
    sortedRects: ff(g, L),
    strategy: K
  }), [i, R, t.draggable, t.droppable, l, g, F0, L, V, K]);
  return g6.default.createElement(xk.Provider, {
    value: $0
  }, J);
}
var uf = (Q) => {
  let {
    id: J,
    items: Y,
    activeIndex: W,
    overIndex: K
  } = Q;
  return _q(Y, W, K).indexOf(J);
}, cf = (Q) => {
  let {
    containerId: J,
    isSorting: Y,
    wasDragging: W,
    index: K,
    items: z,
    newIndex: N,
    previousItems: F,
    previousContainerId: L,
    transition: w
  } = Q;
  if (!w || !W)
    return !1;
  if (F !== z && K === N)
    return !1;
  if (Y)
    return !0;
  return N !== K && J === L;
}, pf = {
  duration: 200,
  easing: "ease"
}, vk = "transform", df = /* @__PURE__ */ GX.Transition.toString({
  property: vk,
  duration: 0,
  easing: "linear"
}), lf = {
  roleDescription: "sortable"
};
function nf(Q) {
  let {
    disabled: J,
    index: Y,
    node: W,
    rect: K
  } = Q, [z, N] = g6.useState(null), F = g6.useRef(Y);
  return cQ(() => {
    if (!J && Y !== F.current && W.current) {
      let L = K.current;
      if (L) {
        let w = c$(W.current, {
          ignoreTransform: !0
        }), D = {
          x: L.left - w.left,
          y: L.top - w.top,
          scaleX: L.width / w.width,
          scaleY: L.height / w.height
        };
        if (D.x || D.y)
          N(D);
      }
    }
    if (Y !== F.current)
      F.current = Y;
  }, [J, Y, W, K]), g6.useEffect(() => {
    if (z)
      N(null);
  }, [z]), z;
}
function hk(Q) {
  let {
    animateLayoutChanges: J = cf,
    attributes: Y,
    disabled: W,
    data: K,
    getNewIndex: z = uf,
    id: N,
    strategy: F,
    resizeObserverConfig: L,
    transition: w = pf
  } = Q, {
    items: D,
    containerId: R,
    activeIndex: V,
    disabled: g,
    disableTransforms: s,
    sortedRects: i,
    overIndex: F0,
    useDragOverlay: r,
    strategy: J0
  } = g6.useContext(xk), l = sf(W, g), t = D.indexOf(N), $0 = g6.useMemo(() => ({
    sortable: {
      containerId: R,
      index: t,
      items: D
    },
    ...K
  }), [R, K, t, D]), M0 = g6.useMemo(() => D.slice(D.indexOf(N)), [D, N]), {
    rect: c0,
    node: I0,
    isOver: p,
    setNodeRef: o
  } = WK({
    id: N,
    data: $0,
    disabled: l.droppable,
    resizeObserverConfig: {
      updateMeasurementsFor: M0,
      ...L
    }
  }), {
    active: Y0,
    activatorEvent: A0,
    activeNodeRect: P0,
    attributes: Y1,
    setNodeRef: N0,
    listeners: W0,
    isDragging: v0,
    over: n1,
    setActivatorNodeRef: g1,
    transform: s1
  } = Ik({
    id: N,
    data: $0,
    attributes: {
      ...lf,
      ...Y
    },
    disabled: l.draggable
  }), _1 = sD(o, N0), U1 = Boolean(Y0), x0 = U1 && !s && tH(V) && tH(F0), N6 = !r && v0, C6 = N6 && x0 ? s1 : null, o1 = F != null ? F : J0, f1 = x0 ? C6 != null ? C6 : o1({
    rects: i,
    activeNodeRect: P0,
    activeIndex: V,
    overIndex: F0,
    index: t
  }) : null, E6 = tH(V) && tH(F0) ? z({
    id: N,
    items: D,
    activeIndex: V,
    overIndex: F0
  }) : t, x1 = Y0 == null ? void 0 : Y0.id, l0 = g6.useRef({
    activeId: x1,
    items: D,
    newIndex: E6,
    containerId: R
  }), i1 = D !== l0.current.items, Z0 = J({
    active: Y0,
    containerId: R,
    isDragging: v0,
    isSorting: U1,
    id: N,
    index: t,
    items: D,
    newIndex: l0.current.newIndex,
    previousItems: l0.current.items,
    previousContainerId: l0.current.containerId,
    transition: w,
    wasDragging: l0.current.activeId != null
  }), F6 = nf({
    disabled: !Z0,
    index: t,
    node: I0,
    rect: c0
  });
  return g6.useEffect(() => {
    if (U1 && l0.current.newIndex !== E6)
      l0.current.newIndex = E6;
    if (R !== l0.current.containerId)
      l0.current.containerId = R;
    if (D !== l0.current.items)
      l0.current.items = D;
  }, [U1, E6, R, D]), g6.useEffect(() => {
    if (x1 === l0.current.activeId)
      return;
    if (x1 && !l0.current.activeId) {
      l0.current.activeId = x1;
      return;
    }
    let v1 = setTimeout(() => {
      l0.current.activeId = x1;
    }, 50);
    return () => clearTimeout(v1);
  }, [x1]), {
    active: Y0,
    activeIndex: V,
    attributes: Y1,
    data: $0,
    rect: c0,
    index: t,
    newIndex: E6,
    items: D,
    isOver: p,
    isSorting: U1,
    isDragging: v0,
    listeners: W0,
    node: I0,
    overIndex: F0,
    over: n1,
    setNodeRef: _1,
    setActivatorNodeRef: g1,
    setDroppableNodeRef: o,
    setDraggableNodeRef: N0,
    transform: F6 != null ? F6 : f1,
    transition: C1()
  };
  function C1() {
    if (F6 || i1 && l0.current.newIndex === t)
      return df;
    if (N6 && !Cq(A0) || !w)
      return;
    if (U1 || Z0)
      return GX.Transition.toString({
        ...w,
        property: vk
      });
    return;
  }
}
function sf(Q, J) {
  var Y, W;
  if (typeof Q === "boolean")
    return {
      draggable: Q,
      droppable: !1
    };
  return {
    draggable: (Y = Q == null ? void 0 : Q.draggable) != null ? Y : J.draggable,
    droppable: (W = Q == null ? void 0 : Q.droppable) != null ? W : J.droppable
  };
}
function eH(Q) {
  if (!Q)
    return !1;
  let J = Q.data.current;
  if (J && "sortable" in J && typeof J.sortable === "object" && "containerId" in J.sortable && "items" in J.sortable && "index" in J.sortable)
    return !0;
  return !1;
}
var of = [M1.Down, M1.Right, M1.Up, M1.Left], Q7 = (Q, J) => {
  let {
    context: {
      active: Y,
      collisionRect: W,
      droppableRects: K,
      droppableContainers: z,
      over: N,
      scrollableAncestors: F
    }
  } = J;
  if (of.includes(Q.code)) {
    if (Q.preventDefault(), !Y || !W)
      return;
    let L = [];
    z.getEnabled().forEach((R) => {
      if (!R || R != null && R.disabled)
        return;
      let V = K.get(R.id);
      if (!V)
        return;
      switch (Q.code) {
        case M1.Down:
          if (W.top < V.top)
            L.push(R);
          break;
        case M1.Up:
          if (W.top > V.top)
            L.push(R);
          break;
        case M1.Left:
          if (W.left > V.left)
            L.push(R);
          break;
        case M1.Right:
          if (W.left < V.left)
            L.push(R);
          break;
      }
    });
    let w = Nk({
      active: Y,
      collisionRect: W,
      droppableRects: K,
      droppableContainers: L,
      pointerCoordinates: null
    }), D = iE(w, "id");
    if (D === (N == null ? void 0 : N.id) && w.length > 1)
      D = w[1].id;
    if (D != null) {
      let R = z.get(Y.id), V = z.get(D), g = V ? K.get(V.id) : null, s = V == null ? void 0 : V.node.current;
      if (s && g && R && V) {
        let F0 = YK(s).some((M0, c0) => F[c0] !== M0), r = yk(R, V), J0 = af(R, V), l = F0 || !r ? {
          x: 0,
          y: 0
        } : {
          x: J0 ? W.width - g.width : 0,
          y: J0 ? W.height - g.height : 0
        }, t = {
          x: g.left,
          y: g.top
        };
        return l.x && l.y ? t : b$(t, l);
      }
    }
  }
  return;
};
function yk(Q, J) {
  if (!eH(Q) || !eH(J))
    return !1;
  return Q.data.current.sortable.containerId === J.data.current.sortable.containerId;
}
function af(Q, J) {
  if (!eH(Q) || !eH(J))
    return !1;
  if (!yk(Q, J))
    return !1;
  return Q.data.current.sortable.index < J.data.current.sortable.index;
}

// src/components/SortableList/components/SortableOverlay/SortableOverlay.tsx
var fk = D6(LQ(), 1), rf = {
  sideEffects: QF({
    styles: {
      active: {
        opacity: "0.4"
      }
    }
  })
};
function Z7({ children: Q }) {
  return /* @__PURE__ */ fk.default.createElement(_k, {
    dropAnimation: rf
  }, Q);
}

// src/ContigsOrganizer.tsx
var dR = D6(gR(), 1);

// src/utils.ts
var vR = (Q, J = 1) => {
  if (Q = (Q ?? "#6d6d6d").replace(/^#/, ""), Q.length !== 6)
    Q = "6d6d6d";
  let Y = parseInt(Q.substring(0, 2), 16), W = parseInt(Q.substring(2, 4), 16), K = parseInt(Q.substring(4, 6), 16);
  return {
    r: Y,
    g: W,
    b: K,
    a: J
  };
};
var xR = (Q) => {
  if (Q.length === 0)
    return null;
  let J = Q.find((Y) => Y.atom === "CA");
  if (!J || !J.x || !J.y || !J.z)
    return null;
  return { x: J.x, y: J.y, z: J.z };
}, hR = (Q) => {
  let J = Q[0], Y = Q[Q.length - 1] - J + 1;
  return Array.from(new Array(Y), (K, z) => z + J);
}, yR = {
  ALA: "A",
  ARG: "R",
  ASN: "N",
  ASP: "D",
  CYS: "C",
  GLU: "E",
  GLN: "Q",
  GLY: "G",
  HIS: "H",
  ILE: "I",
  LEU: "L",
  LYS: "K",
  MET: "M",
  PHE: "F",
  PRO: "P",
  SER: "S",
  THR: "T",
  TRP: "W",
  TYR: "Y",
  VAL: "V",
  "?": "?"
}, FX = (Q) => {
  if (Q === void 0)
    return !1;
  return Q.toLowerCase() === Q.toUpperCase();
}, gq = (Q) => {
  let J = /^([A-Z]+)(\d+)(-\d+)?$/, Y = Q.match(J);
  if (!Y)
    return console.error("The regex cannot parse this segment: " + Q), null;
  let [, W, K, z] = Y, N = parseInt(K, 10), F = z ? parseInt(z.slice(1), 10) : N;
  if (N > F)
    return console.error("Invalid segment: " + Q), null;
  return {
    chainId: W,
    firstIndex: N,
    lastIndex: F
  };
}, zU = (Q, J) => {
  let Y = Q.filter((K) => !FX(K.content)), W = [];
  for (let K = 0;K < Y.length - 1; K++) {
    let z = gq(Y[K].content), N = gq(Y[K + 1].content);
    if (!z) {
      console.error("Failed parsing distances for this segment: " + Y[K].content);
      continue;
    }
    if (!N) {
      console.error("Failed parsing distances for this segment: " + Y[K + 1].content);
      continue;
    }
    let F = J.filter((V) => V.resSeq === z.lastIndex && V.chainID === z.chainId), L = J.filter((V) => V.resSeq === N.firstIndex && V.chainID === N.chainId), w = xR(F), D = xR(L);
    if (!w) {
      console.error("Failed parsing distances for this segment: " + Y[K].content);
      continue;
    }
    if (!D) {
      console.error("Failed parsing distances for this segment: " + Y[K + 1].content);
      continue;
    }
    let R = Math.sqrt((D.x - w.x) ** 2 + (D.y - w.y) ** 2 + (D.z - w.z) ** 2);
    W.push({ segment: `${z.chainId}${z.lastIndex}_${N.chainId}${N.firstIndex}`, result: R });
  }
  return W;
};

// src/ContigsOrganizerItem.tsx
var yZ = D6(LQ(), 1);

// src/AddSegmentButton.tsx
var qQ = D6(LQ(), 1);
function Eb(Q) {
  let { contigParts: J, index: Y, isGeneratedSegment: W, handleAddContigPart: K, upperButton: z, generatedSegmentConnection: N, label: F } = Q;
  if (F !== void 0)
    return /* @__PURE__ */ qQ.default.createElement("div", {
      className: "contigRowContainer"
    }, /* @__PURE__ */ qQ.default.createElement("div", {
      className: "contigRowColumn1"
    }, /* @__PURE__ */ qQ.default.createElement("button", {
      onClick: () => K(Y),
      className: "add-button"
    }, "+")), /* @__PURE__ */ qQ.default.createElement("div", {
      className: "contigRowColumn2"
    }, F));
  let L = J.filter((t) => !t.unindexed), w = J[Y], D = L.findIndex((t) => t.id === w?.id), R = L[D + 1], V = D === L.length - 1, g = !W(w?.content), s = !W(R?.content), i = z && g, F0 = !z && Y !== void 0 && Y < J.length && g && (V || s), r = V ? "C-term generated segment" : N(Y, !0, ""), J0 = typeof r === "string" && r.toLowerCase().includes("invalid"), l;
  if (J0)
    l = "red";
  else if (V)
    l = "inherit";
  else
    l = "orange";
  return /* @__PURE__ */ qQ.default.createElement(qQ.default.Fragment, null, i && /* @__PURE__ */ qQ.default.createElement("div", {
    className: "contigRowContainer"
  }, /* @__PURE__ */ qQ.default.createElement("div", {
    className: "contigRowColumn1"
  }, /* @__PURE__ */ qQ.default.createElement("button", {
    onClick: () => K(0),
    className: "add-button"
  }, "+")), /* @__PURE__ */ qQ.default.createElement("div", {
    className: "contigRowColumn2"
  }, "N-term generated segment")), F0 && /* @__PURE__ */ qQ.default.createElement("div", {
    className: "contigRowContainer"
  }, /* @__PURE__ */ qQ.default.createElement("div", {
    className: "contigRowColumn1"
  }, /* @__PURE__ */ qQ.default.createElement("button", {
    onClick: () => K(Y + 1),
    className: "add-button"
  }, "+")), /* @__PURE__ */ qQ.default.createElement("div", {
    className: "contigRowColumn2"
  }, /* @__PURE__ */ qQ.default.createElement("span", {
    style: { color: l }
  }, r))));
}
var FK = Eb;

// src/ContigPart.tsx
var mJ = D6(LQ(), 1), Fb = (Q) => {
  let J = mJ.createRef(), [Y, W] = mJ.useState(Q.contigPart), K = (F) => {
    W(F.target.value);
  }, z = () => {
    Q.updateContigPart(Q.index, Y === "" ? null : Y);
  }, N = (F) => {
    if (F.key === "Enter")
      J.current?.blur();
  };
  return mJ.useEffect(() => {
    if (W(Q.contigPart), Q.contigPart === "")
      J.current?.focus();
  }, [Q.contigPart]), /* @__PURE__ */ mJ.default.createElement("input", {
    ref: J,
    type: "text",
    value: Y,
    placeholder: "10 or 10-20",
    onChange: K,
    onBlur: z,
    onKeyDown: N,
    className: "contigPart"
  });
}, fR = Fb;

// src/components/SortableList/SortableList.tsx
var UX = D6(LQ(), 1);

// src/components/SortableList/components/SortableItem/SortableItem.tsx
var hZ = D6(LQ(), 1);
var mR = hZ.createContext({
  attributes: {},
  listeners: void 0,
  ref() {}
});
function bR({ children: Q, id: J, color: Y }) {
  let {
    attributes: W,
    isDragging: K,
    listeners: z,
    setNodeRef: N,
    setActivatorNodeRef: F,
    transform: L,
    transition: w
  } = hk({ id: J }), D = hZ.useMemo(() => ({
    attributes: W,
    listeners: z,
    ref: F
  }), [W, z, F]), R = vR(Y, 0.1), V = {
    opacity: K ? 0.4 : void 0,
    transform: GX.Translate.toString(L),
    transition: w,
    color: Y,
    borderColor: Y,
    backgroundColor: `rgba(${R.r}, ${R.g}, ${R.b}, ${R.a})`
  };
  return /* @__PURE__ */ hZ.default.createElement(mR.Provider, {
    value: D
  }, /* @__PURE__ */ hZ.default.createElement("li", {
    className: "SortableItem",
    ref: N,
    style: V
  }, Q));
}
function uR() {
  let { attributes: Q, listeners: J, ref: Y } = hZ.useContext(mR);
  return /* @__PURE__ */ hZ.default.createElement("button", {
    className: "DragHandle",
    ...Q,
    ...J,
    ref: Y
  }, /* @__PURE__ */ hZ.default.createElement("svg", {
    viewBox: "0 0 20 20",
    width: "12"
  }, /* @__PURE__ */ hZ.default.createElement("path", {
    d: "M7 2a2 2 0 1 0 .001 4.001A2 2 0 0 0 7 2zm0 6a2 2 0 1 0 .001 4.001A2 2 0 0 0 7 8zm0 6a2 2 0 1 0 .001 4.001A2 2 0 0 0 7 14zm6-8a2 2 0 1 0-.001-4.001A2 2 0 0 0 13 6zm0 2a2 2 0 1 0 .001 4.001A2 2 0 0 0 13 8zm0 6a2 2 0 1 0 .001 4.001A2 2 0 0 0 13 14z"
  })));
}

// src/components/SortableList/SortableList.tsx
function UK({
  items: Q,
  onChange: J,
  renderItem: Y
}) {
  let [W, K] = UX.useState(null), z = UX.useMemo(() => Q.find((F) => F.id === W?.id), [W, Q]), N = nH(Iq(d$), Iq(p$, {
    coordinateGetter: Q7
  }));
  return /* @__PURE__ */ UX.default.createElement(iH, {
    sensors: N,
    onDragStart: ({ active: F }) => {
      K(F);
    },
    onDragEnd: ({ active: F, over: L }) => {
      if (L && F.id !== L?.id) {
        let w = Q.findIndex(({ id: R }) => R === F.id), D = Q.findIndex(({ id: R }) => R === L.id);
        J(_q(Q, w, D));
      }
      K(null);
    },
    onDragCancel: () => {
      K(null);
    }
  }, /* @__PURE__ */ UX.default.createElement(KK, {
    items: Q
  }, /* @__PURE__ */ UX.default.createElement("ul", {
    className: "SortableList",
    role: "application"
  }, Q.map((F, L) => /* @__PURE__ */ UX.default.createElement(UX.default.Fragment, {
    key: F.id
  }, Y(F, L))))), /* @__PURE__ */ UX.default.createElement(Z7, null, z ? Y(z) : null));
}
UK.Item = bR;
UK.DragHandle = uR;

// src/ContigsOrganizerItem.tsx
function Ub(Q) {
  let { idx: J, isGeneratedSegment: Y, contigParts: W, handleAddContigPart: K, generatedSegmentConnection: z, item: N, getFixedSegmentDescription: F, updateContigPart: L, getColor: w, hideAddButtons: D } = Q, R = !Y(N.content), V = R ? F(N.content) : z(J, !1, N.content), g = "inherit";
  if (typeof V === "string" && V.toLowerCase().includes("invalid"))
    g = "red";
  return /* @__PURE__ */ yZ.default.createElement(yZ.default.Fragment, null, !D && Q.idx === 0 && /* @__PURE__ */ yZ.default.createElement(FK, {
    index: Q.idx,
    handleAddContigPart: K,
    contigParts: W,
    isGeneratedSegment: Y,
    upperButton: !0,
    generatedSegmentConnection: z
  }), /* @__PURE__ */ yZ.default.createElement("div", {
    className: "contigRowContainer"
  }, /* @__PURE__ */ yZ.default.createElement("div", {
    className: "contigRowColumn1",
    style: { display: "block" }
  }, /* @__PURE__ */ yZ.default.createElement(UK.Item, {
    id: N.id,
    color: w(N)
  }, /* @__PURE__ */ yZ.default.createElement(fR, {
    contigPart: N.content,
    index: J,
    updateContigPart: L
  }), R && /* @__PURE__ */ yZ.default.createElement(UK.DragHandle, null))), J !== void 0 && /* @__PURE__ */ yZ.default.createElement("div", {
    className: "contigRowColumn2"
  }, /* @__PURE__ */ yZ.default.createElement("span", {
    style: { color: g }
  }, V))), !D && J !== void 0 && J < W.length && /* @__PURE__ */ yZ.default.createElement(FK, {
    index: J,
    handleAddContigPart: K,
    contigParts: W,
    isGeneratedSegment: Y,
    upperButton: !1,
    generatedSegmentConnection: z
  }));
}
var cR = Ub;

// node_modules/uuid/dist/esm-browser/stringify.js
var u8 = [];
for (let Q = 0;Q < 256; ++Q)
  u8.push((Q + 256).toString(16).slice(1));
function pR(Q, J = 0) {
  return (u8[Q[J + 0]] + u8[Q[J + 1]] + u8[Q[J + 2]] + u8[Q[J + 3]] + "-" + u8[Q[J + 4]] + u8[Q[J + 5]] + "-" + u8[Q[J + 6]] + u8[Q[J + 7]] + "-" + u8[Q[J + 8]] + u8[Q[J + 9]] + "-" + u8[Q[J + 10]] + u8[Q[J + 11]] + u8[Q[J + 12]] + u8[Q[J + 13]] + u8[Q[J + 14]] + u8[Q[J + 15]]).toLowerCase();
}

// node_modules/uuid/dist/esm-browser/rng.js
var NU, Pb = new Uint8Array(16);
function EU() {
  if (!NU) {
    if (typeof crypto === "undefined" || !crypto.getRandomValues)
      throw new Error("crypto.getRandomValues() not supported. See https://github.com/uuidjs/uuid#getrandomvalues-not-supported");
    NU = crypto.getRandomValues.bind(crypto);
  }
  return NU(Pb);
}

// node_modules/uuid/dist/esm-browser/native.js
var Ab = typeof crypto !== "undefined" && crypto.randomUUID && crypto.randomUUID.bind(crypto), FU = { randomUUID: Ab };

// node_modules/uuid/dist/esm-browser/v4.js
function Lb(Q, J, Y) {
  if (FU.randomUUID && !J && !Q)
    return FU.randomUUID();
  Q = Q || {};
  let W = Q.random ?? Q.rng?.() ?? EU();
  if (W.length < 16)
    throw new Error("Random bytes length must be >= 16");
  if (W[6] = W[6] & 15 | 64, W[8] = W[8] & 63 | 128, J) {
    if (Y = Y || 0, Y < 0 || Y + 16 > J.length)
      throw new RangeError(`UUID byte range ${Y}:${Y + 15} is out of buffer bounds`);
    for (let K = 0;K < 16; ++K)
      J[Y + K] = W[K];
    return J;
  }
  return pR(W);
}
var PK = Lb;
// src/ContigsOrganizer.tsx
var W7 = "unindexed-dropzone", K7 = "indexed-dropzone";
function Ob({ children: Q, isEmpty: J }) {
  let { setNodeRef: Y, isOver: W } = WK({ id: W7 }), K = [
    "unindexedSection",
    W ? "unindexedSectionOver" : ""
  ].filter(Boolean).join(" ");
  return /* @__PURE__ */ D1.default.createElement("div", {
    ref: Y,
    className: K
  }, J ? /* @__PURE__ */ D1.default.createElement("div", {
    className: "emptySectionPlaceholder"
  }, "Drag fixed segments here to let RFdiffusion3 decide their sequence position") : /* @__PURE__ */ D1.default.createElement("ul", {
    className: "SortableList"
  }, Q), /* @__PURE__ */ D1.default.createElement("div", {
    className: "unindexedSectionHeader"
  }, "Unindexed motif residues: kept structurally, RFdiffusion3 decides their sequence position within the generated segments"));
}
function wb({ children: Q, isEmpty: J, onAddSegment: Y }) {
  let { setNodeRef: W, isOver: K } = WK({ id: K7 });
  if (!J)
    return /* @__PURE__ */ D1.default.createElement("ul", {
      className: "SortableList",
      role: "application"
    }, Q);
  return /* @__PURE__ */ D1.default.createElement("div", {
    ref: W,
    className: `indexedSectionEmpty ${K ? "indexedSectionOver" : ""}`
  }, /* @__PURE__ */ D1.default.createElement(FK, {
    index: 0,
    handleAddContigPart: Y,
    contigParts: [],
    isGeneratedSegment: FX,
    upperButton: !1,
    generatedSegmentConnection: () => "",
    label: "Add generated segment"
  }));
}
function Mb(Q) {
  let [J, Y] = D1.useState(), [W, K] = D1.useState([]), [z, N] = D1.useState(null), F = D1.useRef(null), L = D1.useRef(/* @__PURE__ */ new Map), w = D1.useRef(/* @__PURE__ */ new Map), D = nH(Iq(d$), Iq(p$, { coordinateGetter: Q7 })), R = Array.from(Q.unindexedSegments).sort().join(",");
  D1.useEffect(() => {
    let p = (Q.contigs ? Q.contigs.split("/") : []).map((A0) => ({
      id: PK(),
      content: A0,
      unindexed: !1
    })), o = Array.from(Q.unindexedSegments).map((A0) => ({
      id: PK(),
      content: A0,
      unindexed: !0
    })), Y0 = [...p, ...o];
    if (Y(Y0), W.length === 0) {
      let A0 = new dR.PdbParser;
      A0.collect(Q.pdb.split(`
`));
      let Y1 = A0.parse().coordinate.atoms.map((W0) => W0.data);
      K(Y1), zU(Y0, Y1).forEach((W0) => L.current.set(W0.segment, W0.result));
    }
  }, [Q.contigs, R]);
  let V = (p, o) => {
    let Y0 = [...p];
    for (let P0 = 0;P0 < Y0.length - 1; P0++)
      if (!Y0[P0].unindexed && !Y0[P0 + 1].unindexed && FX(Y0[P0].content) && FX(Y0[P0 + 1].content))
        Y0.splice(P0, 1), P0--;
    return zU(p, o).forEach((P0) => L.current.set(P0.segment, P0.result)), Y0;
  }, g = (p) => {
    let o = { id: PK(), content: "", unindexed: !1 };
    Y((Y0) => {
      let A0 = [...Y0 || []];
      return A0.splice(p, 0, o), V(A0, W);
    });
  }, s = (p, o) => {
    Y((Y0) => {
      let A0 = [...Y0 || []];
      if (o === null)
        A0.splice(p, 1);
      else
        A0[p].content = o;
      return V(A0, W);
    });
  }, i = (p) => {
    if (p.unindexed)
      return "#ab9a1d";
    let o = Q.colors.get(p.content);
    if (o)
      return o;
    return "#6d6d6d";
  }, F0 = (p, o, Y0) => {
    if (J === void 0)
      return "";
    let A0 = J.filter((s1) => !s1.unindexed), P0 = A0.findIndex((s1) => s1.id === J[p]?.id);
    if (!o && P0 === 0)
      return A0.length === 1 ? "Generated segment" : "N-term generated segment";
    if (P0 === A0.length - 1)
      return "C-term generated segment";
    let Y1 = o ? A0[P0].content : A0[P0 - 1].content, N0 = A0[P0 + 1]?.content ?? "";
    if (FX(Y1) || FX(N0))
      return "";
    let W0 = gq(Y1), v0 = gq(N0);
    if (!W0)
      return console.error("Failed parsing distances for this segment: " + Y1), `Invalid connected fixed segment ${Y1}. Please, change it.`;
    if (!v0)
      return console.error("Failed parsing distances for this segment: " + N0), `Invalid connected fixed segment ${N0}. Please, change it.`;
    let n1 = L.current.get(`${W0.chainId}${W0.lastIndex}_${v0.chainId}${v0.firstIndex}`)?.toFixed(1) ?? "?";
    if (o || !Y0)
      return `Please add a segment connecting ${W0.chainId}${W0.lastIndex} -> ${v0.chainId}${v0.firstIndex} (${n1} Å)`;
    let g1 = Y0.match(/^[A-Z]?([0-9]+)(-([0-9]+))?$/);
    if (g1) {
      if (parseInt(g1[1]) > parseInt(g1[3] || g1[1]))
        return "Invalid range (start > end)";
    } else
      return "Invalid format, expected: 10, 10-20, or A10-20";
    return /* @__PURE__ */ D1.default.createElement(D1.default.Fragment, null, "Generated segment of ", Y0, " residues", /* @__PURE__ */ D1.default.createElement("br", null), /* @__PURE__ */ D1.default.createElement("span", null, "Connecting ", W0.chainId, W0.lastIndex, " -> ", v0.chainId, v0.firstIndex, " (", n1, " Å)"));
  }, r = (p) => {
    if (w.current.has(p)) {
      let W0 = w.current.get(p);
      if (W0.length >= 10)
        return `Fixed segment of ${W0.length} residues: ${W0.substring(0, 3)}...${W0.substring(W0.length - 3, W0.length)}`;
      return `Fixed segment of ${W0.length} residues: ${W0}`;
    }
    let Y0 = gq(p);
    if (!Y0)
      return "Invalid segment. Please, change it.";
    let A0 = hR([Y0.firstIndex, Y0.lastIndex]), N0 = W.filter((W0) => W0.chainID === Y0.chainId && A0.indexOf(W0.resSeq ?? -1) !== -1).reduce((W0, v0) => {
      if (W0.length === 0 || W0[W0.length - 1].resName !== v0.resName || W0[W0.length - 1].resSeq !== v0.resSeq)
        W0.push(v0);
      return W0;
    }, []).map((W0) => yR[W0.resName]).join("");
    if (w.current.set(p, N0), N0.length >= 10)
      return `Fixed segment of length ${N0.length}: ${N0.substring(0, 3)}...${N0.substring(N0.length - 3, N0.length)}`;
    return `Fixed segment of length ${N0.length}: ${N0}`;
  };
  D1.useEffect(() => {
    if (F.current)
      uQ.setFrameHeight(F.current.clientHeight);
    if (J !== void 0) {
      let p = [];
      for (let o of J) {
        if (o.unindexed)
          continue;
        if (FX(o.content) && p.length > 0 && FX(p[p.length - 1]))
          continue;
        p.push(o.content);
      }
      Q.updateStreamlitComponentValue({
        contig: p.join("/"),
        unindexedSegments: J.filter((o) => o.unindexed).map((o) => o.content)
      });
    }
  }, [F, J]);
  let J0 = D1.useMemo(() => (J ?? []).filter((p) => !p.unindexed), [J]), l = D1.useMemo(() => (J ?? []).filter((p) => p.unindexed), [J]), t = (p) => {
    if (p === W7)
      return "unindexed";
    if (p === K7)
      return "indexed";
    if (l.some((o) => o.id === p))
      return "unindexed";
    if (J0.some((o) => o.id === p))
      return "indexed";
    return null;
  }, $0 = ({ active: p, over: o }) => {
    if (N(null), !o)
      return;
    let Y0 = t(p.id), A0 = t(o.id);
    if (!Y0 || !A0)
      return;
    let P0 = (J ?? []).find((_1) => _1.id === p.id);
    if (!P0)
      return;
    if (A0 === "unindexed" && FX(P0.content))
      return;
    if (Y0 === A0) {
      if (p.id === o.id)
        return;
      let _1 = Y0 === "indexed" ? J0 : l, U1 = _1.findIndex((f1) => f1.id === p.id), x0 = _1.findIndex((f1) => f1.id === o.id);
      if (U1 < 0 || x0 < 0)
        return;
      let N6 = _q(_1, U1, x0), C6 = (J ?? []).filter((f1) => Y0 === "indexed" ? f1.unindexed : !f1.unindexed), o1 = Y0 === "indexed" ? [...N6, ...C6] : [...C6, ...N6];
      Y(V(o1, W));
      return;
    }
    let Y1 = { ...P0, unindexed: A0 === "unindexed" }, N0 = (Y0 === "indexed" ? J0 : l).filter((_1) => _1.id !== p.id), W0 = A0 === "indexed" ? J0 : l, v0;
    if (o.id === W7 || o.id === K7)
      v0 = W0.length;
    else if (v0 = W0.findIndex((_1) => _1.id === o.id), v0 < 0)
      v0 = W0.length;
    let n1 = [...W0];
    n1.splice(v0, 0, Y1);
    let g1 = A0 === "indexed" ? n1 : N0, s1 = A0 === "unindexed" ? n1 : N0;
    Y(V([...g1, ...s1], W));
  };
  if (J === void 0)
    return /* @__PURE__ */ D1.default.createElement("div", {
      ref: F
    });
  let M0 = (p) => J.findIndex((o) => o.id === p.id), c0 = J.find((p) => p.id === z?.id), I0 = (p, o) => /* @__PURE__ */ D1.default.createElement(cR, {
    key: p.id,
    idx: M0(p),
    handleAddContigPart: g,
    contigParts: J,
    isGeneratedSegment: FX,
    generatedSegmentConnection: F0,
    item: p,
    getFixedSegmentDescription: r,
    getColor: i,
    updateContigPart: s,
    hideAddButtons: o
  });
  return /* @__PURE__ */ D1.default.createElement("div", {
    ref: F
  }, /* @__PURE__ */ D1.default.createElement(iH, {
    sensors: D,
    onDragStart: ({ active: p }) => N(p),
    onDragEnd: $0,
    onDragCancel: () => N(null)
  }, /* @__PURE__ */ D1.default.createElement(KK, {
    items: J0.length > 0 ? J0 : [K7]
  }, /* @__PURE__ */ D1.default.createElement(wb, {
    isEmpty: J0.length === 0,
    onAddSegment: g
  }, J0.map((p) => I0(p, !1)))), /* @__PURE__ */ D1.default.createElement(KK, {
    items: l.length > 0 ? l : [W7]
  }, /* @__PURE__ */ D1.default.createElement(Ob, {
    isEmpty: l.length === 0
  }, l.map((p) => I0(p, !0)))), /* @__PURE__ */ D1.default.createElement(Z7, null, c0 ? I0(c0, !0) : null)));
}
var lR = Mb;

// src/StreamlitWrapper.tsx
class sR extends bE {
  constructor(Q) {
    super(Q);
    this.state = { currentComponentState: null }, this.updateStreamlitComponentValue = this.updateStreamlitComponentValue.bind(this);
  }
  updateStreamlitComponentValue = (Q) => {
    this.setState((J) => {
      if (J?.currentComponentState) {
        let Y = JSON.stringify(J.currentComponentState), W = JSON.stringify(Q);
        if (Y !== W)
          uQ.setComponentValue({
            previous: J.currentComponentState,
            current: Q
          });
      }
      return {
        ...J,
        currentComponentState: Q
      };
    });
  };
  render = () => {
    let Q = this.props.args.contigs, J = this.props.args.pdb, Y = new Map(Object.entries(JSON.parse(this.props.args.colors))), W = new Set(JSON.parse(this.props.args.unindexed_segments ?? "[]"));
    if (!(Q && Q.trim() !== "") && W.size === 0)
      return "No contigs provided.";
    return /* @__PURE__ */ nR.default.createElement(lR, {
      contigs: Q ?? "",
      pdb: J,
      colors: Y,
      unindexedSegments: W,
      updateStreamlitComponentValue: this.updateStreamlitComponentValue
    });
  };
}
var oR = uE(sR);

// src/index.tsx
var Db = document.getElementById("root"), kb = aR.createRoot(Db);
kb.render(/* @__PURE__ */ H7.default.createElement(H7.default.StrictMode, null, /* @__PURE__ */ H7.default.createElement(oR, null)));
