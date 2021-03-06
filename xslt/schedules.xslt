 <xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">



    <xsl:template match="schedule.group">
      <div class="schedule-group">
                <xsl:if test="@data-hook!=''">
                    <xsl:attribute name="data-hook">
                        <xsl:value-of select="@data-hook"/>
                    </xsl:attribute>
                    <xsl:attribute name="data-hook-length">
                        <xsl:value-of select="@data-hook-length"/>
                    </xsl:attribute>
                </xsl:if>
        <xsl:apply-templates select="schedule"/>
      </div>
    </xsl:template>

    <xsl:template match="schedule.provisions">
      <div class="schedule-provisions">
            <xsl:if test="@data-hook!=''">
                <xsl:attribute name="data-hook">
                    <xsl:value-of select="@data-hook"/>
                </xsl:attribute>
                <xsl:attribute name="data-hook-length">
                    <xsl:value-of select="@data-hook-length"/>
                </xsl:attribute>
            </xsl:if>
        <xsl:apply-templates select="prov|part|schedule.group"/>
      </div>
    </xsl:template>

    <xsl:template match="schedule.misc">
      <div class="schedule-misc">
        <xsl:apply-templates select="head1|para|prov"/>
      </div>
    </xsl:template>

    <xsl:template match="schedule.forms">
      <div class="schedule-forms">
        <xsl:apply-templates select="form"/>
      </div>
    </xsl:template>

    <xsl:template match="schedule.amendments">
      <div class="schedule-amendments">
        <xsl:apply-templates />
      </div>
    </xsl:template>

    <xsl:template match="schedule.amendments.group1">
      <div class="schedule-amendments-group1">
        <xsl:attribute name="id">
              <xsl:value-of select="@id"/>
          </xsl:attribute>
        <h2 class="schedule-amendments-group1"><xsl:apply-templates select="heading"/></h2>
        <xsl:apply-templates select="schedule.amendments.group2"/>
      </div>
  </xsl:template>

    <xsl:template match="schedule.amendments.group2">
      <div class="schedule-amendments-group2">
        <xsl:attribute name="id">
              <xsl:value-of select="@id"/>
          </xsl:attribute>
        <xsl:apply-templates />
      </div>
    </xsl:template>

    <xsl:template match="schedule.amendments.group2/heading">
        <h5 class="schedule-amendments-group2">
             <xsl:apply-templates />
        </h5>
    </xsl:template>


    <xsl:template match="schedule">
        <div class="schedule">
            <xsl:if test="@data-hook!=''">
                <xsl:attribute name="data-hook">
                    <xsl:value-of select="@data-hook"/>
                </xsl:attribute>
                <xsl:attribute name="data-hook-length">
                    <xsl:value-of select="@data-hook-length"/>
                </xsl:attribute>
            </xsl:if>
            <xsl:call-template name="current"/>
            <xsl:attribute name="id">
                <xsl:value-of select="@id"/>
            </xsl:attribute>
            <xsl:attribute name="data-location">
              <xsl:if test="ancestor::schedule">&#160;</xsl:if>
                <xsl:choose>
                  <xsl:when test="label[normalize-space(.) != '']">sch <xsl:value-of select="normalize-space(label)"/></xsl:when>
                  <xsl:otherwise>sch</xsl:otherwise>
                  </xsl:choose>
              </xsl:attribute>

                        <h2 class="schedule">
                            <span class="label">Schedule<xsl:if test="./label/text()!='Schedule'">&#160;<xsl:value-of select="label"/></xsl:if>
                            </span>
                            <xsl:value-of select="heading"/>
                        </h2>

            <xsl:apply-templates />
        </div>
    </xsl:template>

    <xsl:template match="schedule/label|schedule/heading">
    </xsl:template>


  </xsl:stylesheet>