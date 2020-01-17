from django.db import models


APERTURES = [('0', '4'), ('1', '4.5'), ('2', '5'), ('3', '5.6'), ('4', '6.3'), ('5', '7.1'), ('6', '8'),
             ('7', '9'), ('8', '10'), ('9', '11'), ('10', '13'), ('11', '14'), ('12', '16'), ('13', '18'),
             ('14', '20'), ('15', '22')]

EXPOSURES = [('9', '5'), ('10', '4'), ('11', '3.2'), ('12', '2.5'), ('13', '2'), ('14', '1.6'), ('15', '1.3'),
             ('16', '1'), ('17', '0.8'), ('18', '0.6'), ('19', '0.5'), ('20', '0.4'), ('21', '0.3'), ('22', '1/4'),
             ('23', '1/5'), ('24', '1/6'), ('25', '1/8'), ('26', '1/10'), ('27', '1/13'), ('28', '1/15'),
             ('29', '1/20'), ('30', '1/25'), ('31', '1/30'), ('32', '1/40'), ('33', '1/50'), ('34', '1/60'),
             ('35', '1/80'), ('36', '1/100'), ('43', '1/500'), ('46', '1/1000')]

ISOS = [('0', 'Auto'), ('1', '100'), ('2', '200'), ('3', '400'), ('4', '800'), ('5', '1600'), ('6', '3200'),
        ('7', '6400'), ('8', '12800'), ('9', '25600')]

FORMAT_TYPES = [('0', 'Large Fine JPEG'), ('1', 'Large Normal JPEG'),
                ('2', 'Medium Fine JPEG'), ('3', 'Medium Normal JPEG'),
                ('4', 'Small Fine JPEG'), ('5', 'Small Normal JPEG'),
                ('6', 'Small JPEG'), ('7', 'RAW + Large Fine JPEG'), ('8', 'RAW')]

IMAGE_TYPES = [('0', 'Preview'), ('1', 'Focus'), ('2', 'Full'), ('3', 'Dark')]

# Add Model-Ids to the name?
SHOW_IDS = True


class CaptureFlow(models.Model):
    """
    container to bundle a set of CaptureConfigs
    """
    name = models.CharField(max_length=300, null=True)

    def __str__(self):
        if SHOW_IDS:
            return "[{}] {}".format(self.pk, self.name)
        return self.name


class CaptureConfig(models.Model):
    """
    holds most of a data to capture an image
    """
    description = models.CharField(max_length=300, null=True)

    bulb_time = models.IntegerField(default=0)
    exposure = models.IntegerField(null=True, choices=EXPOSURES, default=EXPOSURES[19][0])
    aperture = models.IntegerField(null=False, choices=APERTURES, default=APERTURES[9][0])
    iso = models.IntegerField(null=False, choices=ISOS)
    image_format = models.IntegerField(null=False, choices=FORMAT_TYPES)

    def get_iso(self):
        return ISOS[self.iso][1]

    def get_aperture(self):
        return APERTURES[self.aperture][1]

    def get_exposure(self):
        return EXPOSURES[self.exposure][1]

    def get_image_format(self):
        return FORMAT_TYPES[self.image_format][1]

    def __str__(self):
        _id = ''
        if SHOW_IDS:
            _id = "[{}] ".format(self.pk)

        if self.bulb_time != 0:
            return "{}{}(blub: {}s/ {} / iso: {})".format(_id, self.description,
                                                          self.bulb_time, self.get_aperture(), self.get_iso())
        return "{}{}({}s/ {} / iso: {} )".format(_id, self.description, self.get_exposure(),
                                                 self.get_aperture(), self.get_iso())


class ConfigMapping(models.Model):
    """
    mapping table for Many-2-Many-relation between CaptureFlow and CaptureConfig
    also saves how many iterations should be performed, and in which order it will be displayed
    see https://docs.djangoproject.com/en/3.0/topics/db/examples/many_to_many/
    """
    flow = models.ForeignKey(CaptureFlow, on_delete=models.CASCADE)
    config = models.ForeignKey(CaptureConfig, on_delete=models.CASCADE)
    repeats = models.IntegerField(default=1)
    order = models.IntegerField(default=1)

    def __str__(self):
        if SHOW_IDS:
            return "[{}] Map flow[{}] => config[{}]".format(self.pk, self.flow.id, self.config.id)
        return "Map flow[{}] => config[{}]".format(self.flow.id, self.config.id)


class ImageFile(models.Model):
    """
    basic image model - whenever a image is captured this on is created
    """
    filename = models.CharField(max_length=200, null=True)
    path = models.CharField(max_length=300)
    date = models.DateTimeField(auto_now_add=True, blank=True)
    config = models.ForeignKey(CaptureConfig, on_delete=models.CASCADE, null=True)
    type = models.CharField(max_length=100, null=True, choices=IMAGE_TYPES)
    description = models.CharField(max_length=200, null=True)

    def create_as_preview(self, filename):
        self.filename = filename
        self.type = IMAGE_TYPES[0][0][0]

    def create_as_full(self, filename, path, _type, description):
        self.filename = filename
        self.path = path
        self.type = _type
        self.description = description

    def __str__(self):
        if SHOW_IDS:
            return "[{}] {}".format(self.pk, self.filename)
        return self.filename
