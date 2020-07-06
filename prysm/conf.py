"""Configuration for this instance of prysm."""
import copy

import numpy as np

from astropy import units as u

from .wavelengths import HeNe

all_ap_unit_types = (u.Unit, u.core.IrreducibleUnit, u.core.CompositeUnit)


def sanitize_unit(unit, wavelength):
    """Sanitize a unit token, either an astropy unit or a string.

    Parameters
    ----------
    unit : `astropy.Unit` or `str`
        unit or string version of unit
    wavelength : `astropy.Unit`
        a wavelength unit generated by mkwvl or equivalent code

    Returns
    -------
    `astropy.Unit`
        an astropy unit

    """
    if not isinstance(unit, all_ap_unit_types):
        if unit.lower() in ('waves', 'wave', 'λ'):
            unit = wavelength
        else:
            unit = getattr(u, unit)
    else:
        unit = unit

    return unit


def format_unit(unit_or_quantity, fmt):
    """(string) format a unit or quantity.

    Parameters
    ----------
    unit_or_quantity : `astropy.units.Unit` or `astropy.units.Quantity`
        a unit or quantity
    fmt : `str`, {'latex', 'unicode'}
        a string format

    Returns
    -------
    `str`
        string

    """
    if isinstance(unit_or_quantity, all_ap_unit_types):
        return unit_or_quantity.to_string(fmt)
    elif isinstance(unit_or_quantity, u.quantity.Quantity):
        return unit_or_quantity.unit.to_string(fmt)
    else:
        raise ValueError('must be a Unit or Quantity instance.')


class Labels:
    """Labels holder for data instances."""
    def __init__(self, xy_base, z,
                 xy_additions=['X', 'Y'], xy_addition_side='right',
                 addition_joiner=' ',
                 unit_prefix='[',
                 unit_suffix=']',
                 unit_joiner=' '):
        """Create a new Labels instance.

        Parameters
        ----------
        xy_base : `str`
            basic string used to build the X and Y labels
        z : `str`
            z label, stored as self._z to avoid clash with self.z()
        xy_additions : iterable, optional
            text to add to the (x, y) labels
        xy_addition_side : {'left', 'right'. 'l', 'r'}, optional
            side to add the x and y additional text to, left or right
        addition_joiner : `str`, optional
            text used to join the x or y addition
        unit_prefix : `str`, optional
            prefix used to surround the unit text
        unit_suffix : `str`, optional
            suffix used to surround the unit text
        unit_joiner : `str`, optional
            text used to combine the base label and the unit

        """
        self.xy_base, self._z = xy_base, z
        self.xy_additions, self.xy_addition_side = xy_additions, xy_addition_side
        self.addition_joiner = addition_joiner
        self.unit_prefix, self.unit_suffix = unit_prefix, unit_suffix
        self.unit_joiner = unit_joiner

    def _label_factory(self, label, xy_unit, z_unit):
        """Produce complex labels.

        Parameters
        ----------
        label : `str`, {'x', 'y', 'z'}
            label to produce

        Returns
        -------
        `str`
            completed label

        """
        if label in ('x', 'y'):
            if label == 'x':
                xy_pos = 0
            else:
                xy_pos = 1
            label_basics = [self.xy_base]
            if self.xy_addition_side.lower() in ('left', 'l'):
                label_basics.insert(0, self.xy_additions[xy_pos])
            else:
                label_basics.append(self.xy_additions[xy_pos])

            label_ = self.addition_joiner.join(label_basics)
            unit_str = format_unit(xy_unit, config.unit_format)
        else:
            label_ = self._z
            unit_str = format_unit(z_unit, config.unit_format)

        unit_text = ''
        if config.show_units:

            unit_text = unit_text.join([self.unit_prefix,
                                       unit_str,
                                       self.unit_suffix])
        label_ = self.unit_joiner.join([label_, unit_text])
        return label_

    def x(self, xy_unit, z_unit):
        """X label."""
        return self._label_factory('x', xy_unit, z_unit)

    def y(self, xy_unit, z_unit):
        """Y label."""
        return self._label_factory('y', xy_unit, z_unit)

    def z(self, xy_unit, z_unit):
        """Z label."""
        return self._label_factory('z', xy_unit, z_unit)

    def generic(self, xy_unit, z_unit):
        """Label without extra X/Y annotation."""
        base = self.xy_base
        join = self.unit_joiner
        unit = format_unit(xy_unit, config.unit_format)
        prefix = self.unit_prefix
        suffix = self.unit_suffix
        return f'{base}{join}{prefix}{unit}{suffix}'

    def copy(self):
        """(Deep) copy."""
        return copy.deepcopy(self)


rel = u.def_unit(['rel'], format={'latex': 'Rel 1.0', 'unicode': 'Rel 1.0'})

default_phase_units = {'xy': u.mm, 'z': u.nm}
default_interferorgam_units = {'xy': u.pixel, 'z': u.nm}
default_image_units = {'xy': u.mm, 'z': u.adu}
default_mtf_units = {'xy': u.mm ** -1, 'z': rel}
default_ptf_units = {'xy': u.mm ** -1, 'z': u.deg}

xi_eta = ['ξ', 'η']
x_y = ['X', 'Y']
default_pupil_labels = Labels(xy_base='Pupil', z='OPD', xy_additions=xi_eta)
default_interferogram_labels = Labels(xy_base='', z='Height', xy_additions=x_y)
default_convolvable_labels = Labels(xy_base='Image Plane', z='Irradiance', xy_additions=x_y)
default_mtf_labels = Labels(xy_base='Spatial Frequency', z='MTF', xy_additions=x_y)
default_ptf_labels = Labels(xy_base='Spatial Frequency', z='PTF', xy_additions=xi_eta)
default_psd_labels = Labels(xy_base='Spatial Frequency', z='PSD', xy_additions=x_y)


class Config(object):
    """Global configuration of prysm."""
    def __init__(self,
                 precision=64,
                 backend=np,
                 zernike_base=1,
                 Q=2,
                 wavelength=HeNe,
                 phase_cmap='inferno',
                 image_cmap='Greys_r',
                 lw=3,
                 zorder=3,
                 alpha=1,
                 interpolation='lanczos',
                 unit_format='latex_inline',
                 show_units=True,
                 phase_xy_unit=u.mm,
                 phase_z_unit=u.nm,
                 image_xy_unit=u.um,
                 image_z_unit=u.adu,
                 mtf_xy_unit=u.mm ** -1,
                 mtf_z_unit=rel,
                 ptf_xy_unit=u.mm ** -1,
                 ptf_z_unit=u.deg,
                 pupil_labels=default_pupil_labels,
                 interferogram_labels=default_interferogram_labels,
                 convolvable_labels=default_convolvable_labels,
                 mtf_labels=default_mtf_labels,
                 ptf_labels=default_ptf_labels,
                 psd_labels=default_psd_labels):
        """Create a new `Config` object.

        Parameters
        ----------
        precision : `int`
            32 or 64, number of bits of precision
        backend : `str`, {'np'}
            a supported backend.  Current options are only "np" for numpy
        zernike_base : `int`, {0, 1}
            base for zernikes; start at 0 or 1
        Q : `float`
            oversampling parameter for numerical propagations
        phase_cmap : `str`
            colormap used for plotting optical phases
        image_cmap : `str`
            colormap used for plotting greyscale images
        lw : `float`
            linewidth
        zorder : `int`, optional
            zorder used for graphics made with matplotlib
        interpolation : `str`
            interpolation type for 2D plots
        unit_formatter : `str`, optional
            string passed to astropy.units.(unit).to_string
        xylabel_joiner : `str`, optional
            text used to glue together X/Y units and their basic string
        unit_prefix : `str`, optional
            text preceeding the unit's representation, after the joiner
        unit_suffix : `str`, optional
            text following the unit's representation
        unit_joiner : `str`, optional
            text used to glue basic labels and the units together
        show_units : `bool`, optional
            if True, shows units on graphics
        phase_units : `Units`
            default units used for phase-like types
        image_units : `Units`
            default units used for image-like types

        """
        self.chbackend_observers = []
        self.initialized = False
        self.precision = precision
        self.backend = backend
        self.zernike_base = zernike_base
        self.Q = Q
        self.wavelength = wavelength
        self.phase_cmap = phase_cmap
        self.image_cmap = image_cmap
        self.lw = lw
        self.zorder = zorder
        self.alpha = alpha
        self.interpolation = interpolation
        self.unit_format = unit_format
        self.show_units = show_units
        self.phase_xy_unit = phase_xy_unit
        self.phase_z_unit = phase_z_unit
        self.image_xy_unit = image_xy_unit
        self.image_z_unit = image_z_unit
        self.mtf_xy_unit = mtf_xy_unit
        self.mtf_z_unit = mtf_z_unit
        self.ptf_xy_unit = ptf_xy_unit
        self.ptf_z_unit = ptf_z_unit
        self.pupil_labels = pupil_labels
        self.interferogram_labels = interferogram_labels
        self.convolvable_labels = convolvable_labels
        self.mtf_labels = mtf_labels
        self.ptf_labels = ptf_labels
        self.psd_labels = psd_labels
        self.initialized = True

    @property
    def precision(self):
        """Precision used for computations.

        Returns
        -------
        `object` : `numpy.float32` or `numpy.float64`
            precision used

        """
        return self._precision

    @property
    def precision_complex(self):
        """Precision used for complex array computations.

        Returns
        -------
        `object` : `numpy.complex64` or `numpy.complex128`
            precision used for complex arrays

        """
        return self._precision_complex

    @precision.setter
    def precision(self, precision):
        """Adjust precision used by prysm.

        Parameters
        ----------
        precision : `int`, {32, 64}
            what precision to use; either 32 or 64 bits

        Raises
        ------
        ValueError
            if precision is not a valid option

        """
        if precision not in (32, 64):
            raise ValueError('invalid precision.  Precision should be 32 or 64.')

        if precision == 32:
            self._precision = np.float32
            self._precision_complex = np.complex64
        else:
            self._precision = np.float64
            self._precision_complex = np.complex128

    @property
    def backend(self):
        """Backend used."""
        return self._backend

    @backend.setter
    def backend(self, backend):
        """Set the backend used by prysm.

        Parameters
        ----------
        backend : `str`, {'np'}
            backend used for computations

        Raises
        ------
        ValueError
            invalid backend

        """
        for obs in self.chbackend_observers:
            obs(self._backend)

    @property
    def zernike_base(self):
        """Zernike base.

        Returns
        -------
        `int`
            {0, 1}

        """
        return self._zernike_base

    @zernike_base.setter
    def zernike_base(self, base):
        """Zernike base; base-0 or base-1.

        Parameters
        ----------
        base : `int`, {0, 1}
            first index of zernike polynomials

        Raises
        ------
        ValueError
            invalid base given

        """
        if base not in (0, 1):
            raise ValueError('By convention zernike base must be 0 or 1.')

        self._zernike_base = base


config = Config()
