# Getting Started Tutorial: Advanced Library Construction
_In this section, we will build a re-usable n-LED array Block, going through the advanced constructs of generators and port arrays._

> The IDE does not support graphical operations for programmatic constructing circuits.
> However, you can continue to use the IDE for visualization.


## The Naive (but Broken) Approach

The HDL provides the ElementDict construct for giving unique names to a dynamically-sized array of blocks.
An array of LEDs looks like: 
```python
self.led = ElementDict[IndicatorLed]()
for i in range(4):
  self.led[i] = self.Block(IndicatorLed())
  ...
```

You might be tempted to drop the above into a Block and pipe the `int` through as a constructor argument:
```python
# DON'T DO THIS - THIS WON'T WORK
class LedArray(Block):
  def __init__(self, count: int) -> None:
    super().__init__()

    self.led = ElementDict[IndicatorLed]()
    for i in range(count):
      self.led[i] = self.Block(IndicatorLed())
      ...
```

However, there's a few problems with this, which illustrates a few significant ways our HDL model differs from Python:
- When you instantiate a block, for example with `self.Block(LedArray(4))`, it only constructs a block stub.
  As a result, we can't pass parameters into `Blocks` that are concrete values like `int`.
  - This structure allows the compiler to resolve the dataflow and fill out the details when the parameter values are ready, instead of forcing the user to take into account dataflow when ordering their code.
    For example, the `IndicatorLed` generated resistor depends on its input voltage, which depends on the voltage on its signal pin, which isn't available until it's connected.
- All IOs must be static, since classes define a single template block.
  So we can't create different numbers of top-level IOs based on a parameter value.

But, we have ways of achieving the same goals even within the above structure.


## Interface
_In this section, we'll define the block's interface using advanced constructs for library writers._
_This will hopefully also illuminate how some of the existing block generators work under the hood._

**Start by creating an empty block, as done previously:**
```python
class LedArray(Block):
  def __init__(self) -> None:
    super().__init__()
```

### Parameters
First, we'll need to define the block such that it can take a parameter.
This is actually only slight twist on the naive approach:  
```python
class LedArray(Block):
  def __init__(self, count: IntLike) -> None:
    super().__init__()
```

Instead of the constructor argument being a Python type that defines a value like `int`, we use an expression-type.
This defines the type of the parameter being passed but not the value.

> The expression type is a way to refer to the parameter but without giving it a concrete value.
> This is needed since the value is resolved in the compiler and therefore not available in the HDL to the constructor.
> 
> Note that the type is not `IntExpr`, but `IntLike`, which also includes `int`.
> This allows calling the constructor with an `int` value directly, if we just have a static parameterization.


### Port Arrays - Definition
Next, because we will have _n_ LEDs, we will need _n_ IO pins.
While we can't define a separate top-level IO for each LED, we can define a port array IO that is dynamically sized:  
```python
class LedArray(Block):
  @init_in_parent
  def __init__(self, count: IntLike) -> None:
    super().__init__()
    self.ios = self.Port(Vector(DigitalSink.empty()), [Input])
    self.gnd = self.Port(Ground.empty(), [Common])
```

Port arrays are a container port that contain individual ports internally.
As we saw from Part 1, viewed externally, they have no defined size and ports can be requested from them with optional names.
However, from internally, we will be able to define their size, as well as get the names of incoming connections.

> Port arrays require the port type to be undefined.
> Since we have not defined any ports so far, this is only needed for the type and may not have additional data like parameter values.


## Implementation
_In this section, we'll actually implement the circuit generator._

### Generator
First, we will need a way to get the concrete (`int`) value for the LED count.
Generators are a way to defer the implementation of the block until its parameter values are ready, then get the concrete Python version of that parameter for use in the HDL.
**We'll change the base class in our prior code from `Block` to `GeneratorBlock` which provides this functionality**.
```python
class LedArray(GeneratorBlock):
  @init_in_parent
  def __init__(self, count: IntLike) -> None:
    super().__init__()
    self.ios = self.Port(Vector(DigitalSink.empty()), [Input])
    self.gnd = self.Port(Ground.empty(), [Common])
    self.count = self.ArgParameter(count)
    self.generator_param(self.count)
    
  def generate(self) -> None:
    super().generate()
    ...
```

> While here we use generators as a way to get a concrete value for circuit generation (the LED count), generators can also be used to do calculations beyond the operations available with the parameters.
> For example, while we can add two `IntExpr`s (which produces another `IntExpr`), something more complex like square root is not provided.
> For those cases, use a generator to get the parameter's concrete value, where you have access to the full power of Python.
> 
> Generator parameters must be explicitly defined using `self.generator_param(...)`.
> Within `generate`, you can get the concrete value of a generator parameter using `self.get(...)`.

### Port Arrays - Internal
So far, the port array is still empty, so we must define its elements.
With the count available as an int, we can use the `for` loop structure from before:
```python
class LedArray(GeneratorBlock):
  ...
  def generate(self) -> None:
    super().generate()
    for i in range(self.get(self.count)):
      self.ios.append_elt(DigitalSink.empty())
      ...
```

> Port array's `.append_elt(...)` takes in the same arguments as `self.Port(...)`.
> 
> To mark a port array as explicitly having no elements, use `.defined()`:
> 
> ```python
>   class EmptyArrayBlock(Block):
>     def __init__(self) -> None:
>       super().__init__()
>       self.empty_array = self.Port(Vector(DigitalSink.empty()))
>       self.empty_array.defined()
> ```

### Circuit Generation
Instantiate the LEDs and connect them to the IO pin and ground as needed.
`.append_elt(...)` returns the newly created port within the array, which can be used in `self.connect(...)`.

> <details>
>   <summary>At this point, your HDL might look like...</summary>
>
>   ```python
>   class LedArray(GeneratorBlock):
>     @init_in_parent
>     def __init__(self, count: IntLike) -> None:
>       super().__init__()
>       self.ios = self.Port(Vector(DigitalSink.empty()), [Input])
>       self.gnd = self.Port(Ground.empty(), [Common])
>       self.count = self.ArgParameter(count)
>       self.generator_param(self.count)
>   
>     def generate(self) -> None:
>         super().generate()
>         self.led = ElementDict[IndicatorLed]()
>         for i in range(self.get(self.count)):
>           io = self.ios.append_elt(DigitalSink.empty())
>           self.led[i] = self.Block(IndicatorLed())
>           self.connect(io, self.led[i].signal)
>           self.connect(self.gnd, self.led[i].gnd)
>   ```
> </details>


## Putting it All Together

Replace the `for` loop in your top-level design with the single parameterized `LedArray` instantiation, and connect it to the microcontroller:  
```python
class BlinkyExample(SimpleBoardTop):
  def contents(self) -> None:
    ...
    with self.implicit_connect(
            ...
    ) as imp:
      ...
      self.led = imp.Block(LedArray(4))
      self.connect(self.mcu.gpio.request_vector('led'), self.led.ios)
```

As shown above, port arrays can be directly connected together to make parallel connections, and we can request sub-arrays from a port array.
When connecting port arrays together, exactly one must define the array width, which is automatically propagated to the others in the connection.
As a result, the single LED count parameter also drives the connection width and the pins requested from the microcontroller. 

> There are several ways to connect to arrays from externally:
> - As in the first part of the tutorial, we can request individual sub-ports.
> - As seen here, we can request a sub-array.
> - Or as also seen here, we can connect the array as a whole
> 
> For connections, only the types have to match, so you can (as done above) connect a whole array to a requested sub-array, or connect two whole arrays.
> Just remember that in any array connection, there must be exactly array of defined width, and all other arrays will take their widths from that.
> 
> Exception, if connecting an internally-facing array as a whole: it can only be connected to exactly one other externally-facing array. 

When `request_vector` is used, each element's suggested name is the sub-array's suggested name, an underscore (`_`), then the element index.
This is slightly different than the naming we've used for pin assignment so far, so we will need to update the refinements:

```python
class BlinkyExample(SimpleBoardTop):
  ...
  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      ...
      instance_values=[
        (['mcu', 'pin_assigns'], [
          'led_0=26',
          'led_1=27',
          'led_2=28',
          'led_3=29',
        ])
      ])

```

### Additional Resources
Check out these examples of generators:
- [Charlieplexing LED generator](examples/test_ledmatrix.py): a much more advanced version of the LED array that minimizes IO pins to drive LEDs, by allowing one IO pin to drive both a column and row of LEDs.
- [Buck and boost converter generators](electronics_abstract_parts/AbstractPowerConverters.py): the power path generator for these switching DC/DC converters encode well-known design equations using generators.
