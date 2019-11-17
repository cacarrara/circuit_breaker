# Circuit Breaker

> The basic idea behind the circuit breaker is very simple. You wrap a protected function
> call in a circuit breaker object, which monitors for failures. Once the failures reach a
> certain threshold, the circuit breaker trips, and all further calls to the circuit breaker
> return with an error, without the protected call being made at all. Usually you'll also
> want some kind of monitor alert if the circuit breaker trips.

Source: [CircuitBreaker](https://martinfowler.com/bliki/CircuitBreaker.html)